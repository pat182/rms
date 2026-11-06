from datetime import datetime
from ...model import (RestaurantTable)
from ...model.repositories import DiningSessionRepo

from fastapi import HTTPException,Request
from sqlalchemy.ext.asyncio import AsyncSession

class DiningSessionService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.repo = DiningSessionRepo(self.db)
        self.model = self.repo.model

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


