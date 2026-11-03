from ...core.dependencies import get_db
from ...model import DiningSession, RestaurantTable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fastapi import Depends, HTTPException


async def get_or_create_dining_session(
    table_qr: str,
    db: AsyncSession = Depends(get_db),
) -> tuple[DiningSession, bool]:

    stmt = (
        select(RestaurantTable)
        .options(selectinload(RestaurantTable.restaurant))
        .where(RestaurantTable.qr_token == table_qr)
    )

    table = await db.scalar(stmt)

    if not table:
        raise HTTPException(
            status_code=404,
            detail="Invalid table QR code.",
        )

    if not table.is_active:
        raise HTTPException(
            status_code=403,
            detail="This table is currently unavailable.",
        )

    if not table.restaurant or not table.restaurant.is_active:
        raise HTTPException(
            status_code=403,
            detail="This restaurant is currently unavailable.",
        )

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
        return dining_session, False

    dining_session = DiningSession(
        restaurant_table_id=table.id,
        is_active=True,
    )

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

    return dining_session, True