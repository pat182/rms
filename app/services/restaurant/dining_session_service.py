import asyncio
from redis.asyncio import Redis
from datetime import datetime, timezone

from ...core.logger import log_info
from ...core.websocket import manager
from ...model import (RestaurantTable, CustomerOrder, DiningSession)
from ...model.repositories import DiningSessionRepo,CustomerOrderRepo
from ...core.database import SessionLocal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException,Request
from fastapi.encoders import jsonable_encoder

class DiningSessionService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.repo = DiningSessionRepo(self.db)
        self.model = self.repo.model



    async def check_session_ownership(self,session_token: str, device_token: str | None ,redis: Redis)-> bool:
        owner_device_token = await redis.get(
            f"rms:dining_session:{session_token}:owner"
        )
        return owner_device_token == device_token

    async def generate_filter(
            self,
            request: Request,
            restaurant_id: int,
    ) -> list:

        query_param = request.query_params

        filters = [
            self.model.restaurant_table.has(
                RestaurantTable.restaurant_id == restaurant_id
            )
        ]

        is_active = query_param.get("is_active")
        status = query_param.get("status")
        started_from = query_param.get("started_from")
        started_to = query_param.get("started_to")

        if is_active is not None:
            filters.append(
                self.model.is_active == (is_active.lower() == "true")
            )

        if status is not None:
            filters.append(
                self.model.status == status
            )

        try:
            started_from = (
                datetime.fromisoformat(started_from)
                if started_from else None
            )

            started_to = (
                datetime.fromisoformat(started_to)
                if started_to else None
            )
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid date format. Use ISO 8601.",
            )

        if started_from is not None and started_to is not None:
            if started_from > started_to:
                raise HTTPException(
                    status_code=422,
                    detail="'started_from' must not be later than 'started_to'.",
                )

        if started_from is not None:
            filters.append(
                self.model.started_at >= started_from
            )

        if started_to is not None:
            filters.append(
                self.model.started_at <= started_to
            )

        return filters

    async def validate_session(self,session_token:str,table_id:int):

        session_stmt = (
            select(self.model)
            .options(
                selectinload(self.model.restaurant_table)
                .selectinload(RestaurantTable.restaurant)
            )
            .where(
                self.model.session_token == session_token,
                self.model.restaurant_table_id == table_id,
                self.model.is_active.is_(True),
                self.model.status.in_(["verified", "pending"]),
            )
        )

        dining_session = await self.db.scalar(session_stmt)

        if not dining_session:
            raise HTTPException(
                status_code=404,
                detail="Dining session not found."
            )

        # Validate the requested session token
        if session_token is not None:
            if session_token != dining_session.session_token:
                raise HTTPException(
                    status_code=422,
                    detail="Session token did not match.",
                )

            if (dining_session.status == "closed"
                    or dining_session.closed_at is not None
                    or not dining_session.is_active):
                raise HTTPException(

                    status_code=403,
                    detail="Dining session is closed.",
                )

        return dining_session

    async def get_dining_session_order(self,session_token:str) -> CustomerOrder :
        customer_repo = CustomerOrderRepo(self.db)

        customer_order = await customer_repo.get_orders_by_session(session_token)

        return customer_order


    @staticmethod
    def build_dining_sesh_socket_payload(
        dining_sesh: DiningSession,
        event: str = "dining_session_created",
        action: str = "created"
    ):
        return jsonable_encoder(
            {
                "event": event,
                "data": {
                    "dining_session": {
                        "table_id": dining_sesh.restaurant_table.id,
                        "session_id" : dining_sesh.id,
                        "session_token" : dining_sesh.session_token,
                        "table_name": dining_sesh.restaurant_table.table_name,
                        "is_active": dining_sesh.is_active,
                        "started_at": (
                            dining_sesh.started_at.isoformat()
                            if dining_sesh.started_at else None
                        ),
                        "closed_at": (
                            dining_sesh.closed_at.isoformat()
                                if dining_sesh.closed_at else None
                            ),
                        "status": dining_sesh.status,
                    },
                    "action": action
                }
            }
        )



    async def monitor_dining_session(
            self,
            redis,
            dining_session: DiningSession,
            warning_seconds: int = 300,
    ):
        owner_key = f"rms:dining_session:{dining_session.session_token}:owner"
        stmt = (select(DiningSession)
                            .options(
                                selectinload(DiningSession.restaurant_table)
                                .selectinload(RestaurantTable.restaurant)
                            )
                            .where(DiningSession.id == dining_session.id))
        try:
            while True:
                ttl = await redis.ttl(owner_key)

                if ttl == -2:
                    log_info("Dining session has expired: ", dining_session.session_token)
                    break

                if ttl == -1:
                    log_info("Dining session key has no expiration: ", dining_session.session_token)
                    break

                if ttl <= warning_seconds:
                    log_info("Dining session is about to expire: ", dining_session.session_token)
                    async with SessionLocal() as db:
                        session = await db.scalar(stmt.execution_options(populate_existing=True))

                        if not session or not session.is_active:
                            log_info("Dining session is no longer active: ", dining_session.session_token)
                            break

                        await manager.broadcast(
                            f"restaurant:{session.restaurant_table.restaurant_id}",
                            self.build_dining_sesh_socket_payload(
                                session,
                                "dining_session_created",
                                "expiration_warn",
                            ),
                        )

                    await asyncio.sleep(ttl)
                    # Check Redis again after the remaining TTL
                    ttl = await redis.ttl(owner_key)
                    if ttl == -2:
                        async with SessionLocal() as db:
                            session = await db.scalar(stmt.execution_options(populate_existing=True))
                            if session and session.is_active:
                                session.status = "closed"
                                session.is_active = False
                                session.closed_at = datetime.now(timezone.utc)
                                await db.commit()
                                await manager.broadcast(
                                    f"restaurant:{session.restaurant_table.restaurant_id}",
                                    self.build_dining_sesh_socket_payload(session, "dining_session_created", "expired"),
                                )
                                log_info("STATUS", session.status)
                                log_info("Dining session successfully closed: ", session.session_token)
                        break
                    continue

                sleep_time = max(1, ttl - warning_seconds)
                log_info("Monitor sleeping for: ", sleep_time)
                await asyncio.sleep(sleep_time)


        except asyncio.CancelledError:
            log_info("Dining session monitor cancelled: ", dining_session.session_token)
            raise

