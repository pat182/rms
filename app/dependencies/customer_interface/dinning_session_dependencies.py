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
    device_token: str = Header(..., alias="X-DEVICE-TOKEN"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
)->DiningSession:

    table_service = RestaurantTableService(db)

    table = await table_service.validate_table_qr_token(table_qr)

    dining_session_service = DiningSessionService(db)

    dining_session = await dining_session_service.validate_session(session_token,table.id)

    is_owner = await dining_session_service.check_session_ownership(dining_session.session_token, device_token,redis)

    is_approved = await redis.exists(
        f"rms:dining_session:{dining_session.session_token}:approved:{device_token}"
    )

    if not is_owner and not is_approved:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this dining session.",
        )

    return dining_session


async def get_or_create_dining_session(
    table_qr: str,
    device_token: str = Header(..., alias="X-DEVICE-TOKEN"),
    session_token: str | None = Header(
        None,
        alias="X-DINING-SESSION-TOKEN",
    ),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> tuple[DiningSession, bool, bool, bool]:

    table_service = RestaurantTableService(db)
    session_service = DiningSessionService(db)

    table = await table_service.validate_table_qr_token(table_qr)

    await db.execute(
        select(RestaurantTable.id)
        .where(RestaurantTable.id == table.id)
        .with_for_update()
    )

    is_new = False
    dining_session = None

    if session_token:
        try:
            dining_session = await session_service.validate_session(
                session_token,
                table.id,
            )
        except HTTPException as exc:
            if exc.status_code != 404:
                raise


    if not dining_session:
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

    # Create a session only when no active session exists.
    if not dining_session:
        dining_session = DiningSession(
            restaurant_table_id=table.id,
            is_active=True,
        )

        db.add(dining_session)
        await db.flush()

        owner_key = (
            f"rms:dining_session:{dining_session.session_token}:owner"
        )

        try:
            await redis.set(
                owner_key,
                device_token,
                ex=10800,
            )

            await db.commit()

        except Exception:
            await db.rollback()
            await redis.delete(owner_key)
            raise

        dining_session = await db.scalar(
            select(DiningSession)
            .options(
                selectinload(DiningSession.restaurant_table)
                .selectinload(RestaurantTable.restaurant)
            )
            .where(DiningSession.id == dining_session.id)
        )

        is_new = True

    # Check ownership and approval.
    is_owner = await session_service.check_session_ownership(
        dining_session.session_token,
        device_token,
        redis,
    )

    if is_owner:
        is_approved = True
    else:
        is_approved = bool(
            await redis.exists(
                f"rms:dining_session:{dining_session.session_token}:approved:{device_token}"
            )
        )

    return dining_session, is_new, is_owner, is_approved
