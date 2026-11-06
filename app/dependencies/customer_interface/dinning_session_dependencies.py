from ...core.dependencies import get_db
from ...model import DiningSession, RestaurantTable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from fastapi import Depends, HTTPException


async def get_or_create_dining_session(
    table_qr: str,
    session_token: str | None = None,
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
        is_new = False
    else:
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

        is_new = True

    # Validate the requested session token
    if session_token is not None:

        if session_token != dining_session.session_token:
            raise HTTPException(
                status_code=404,
                detail="Dining session not found.",
            )

        if (
            dining_session.status == "closed"
            or dining_session.closed_at is not None
            or not dining_session.is_active
        ):
            raise HTTPException(
                status_code=403,
                detail="Dining session is closed.",
            )

    return dining_session, is_new