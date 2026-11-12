from redis.asyncio import Redis

from .. import get_redis
from ...core.dependencies import get_db
from ...model import DiningSession, RestaurantTable
from ...services.restaurant import RestaurantTableService,DiningSessionService

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fastapi import Depends, HTTPException, Header


async def customer_session_dependency(
    table_qr:str,
    session_token: str,
    db: AsyncSession = Depends(get_db),
)->DiningSession:

    table_service = RestaurantTableService(db)

    table = await table_service.validate_table_qr_token(table_qr)

    dining_session_service = DiningSessionService(db)

    dining_session = await dining_session_service.validate_session(session_token,table.id)

    return dining_session




async def get_or_create_dining_session(
    table_qr: str,
    device_token: str = Header(..., alias="X-DEVICE-TOKEN"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> tuple[DiningSession, bool, bool]:

    table_service = RestaurantTableService(db)

    table = await table_service.validate_table_qr_token(table_qr)

    session_stmt = (
        select(DiningSession)
        .options(
            selectinload(DiningSession.restaurant_table)
            .selectinload(RestaurantTable.restaurant)
        )
        .where(
            DiningSession.restaurant_table_id == table.id,
            DiningSession.is_active.is_(True),
            DiningSession.status.in_(["verified", "pending"]),
        )
    )

    dining_session = await db.scalar(session_stmt)

    if dining_session:
        is_new = False
        owner_device_token = await redis.get(
            f"rms:dining_session:{dining_session.session_token}:owner"
        )
        is_owner = owner_device_token == device_token
        # from app.core.logger import log_info
        # log_info("===============================================")
        # log_info(f"DEVICE TOKEN: {device_token}")
        # log_info(f"OWNER TOKEN: {owner_device_token}")
        # log_info(f"SESSION TOKEN: {dining_session.session_token}")
        # log_info(f"IS OWNER: {is_owner}")
        # log_info("===============================================")

    else:

        dining_session = DiningSession(
            restaurant_table_id=table.id,
            is_active=True,
        )
        # from app.core.logger import log_info
        # log_info(f"NEW SESSION OWNER REGISTERED: {device_token}")
        # log_info(f"NEW SESSION TOKEN: {dining_session.session_token}")

        db.add(dining_session)
        await db.commit()

        dining_session = await db.scalar(
            select(DiningSession)
            .options(
                selectinload(DiningSession.restaurant_table)
                .selectinload(RestaurantTable.restaurant)
            )
            .where(DiningSession.id == dining_session.id)
        )

        is_new = True
        is_owner = True
        await redis.set(
            f"rms:dining_session:{dining_session.session_token}:owner",
            device_token,
            ex=10800,
        )

    return dining_session, is_new, is_owner