from datetime import datetime
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

from ...helper import is_open_today
from ...model import RestaurantTable, Restaurant
from ...model.repositories.restaurant_table_repo import RestaurantTableRepo
from ...schemas.restaurant import CreateRestoRequest, CreateSeshStatusRequest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

class RestaurantTableService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.repo = RestaurantTableRepo(self.db)
        self.model = self.repo.model

    async def get_resto_table(self,table_id:int,restaurant_id:int) -> RestaurantTable:
        table = await self.repo.get_by_id(table_id, restaurant_id)

        if table is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant table not found",
            )

        return table

    async def delete_resto_table(self,table_id:int,restaurant_id:int)->None:
        table = await self.repo.get_by_id_with_sesh(table_id, restaurant_id)
        if table is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant table not found",
            )

        if table.dining_sessions:
            raise HTTPException(
                status_code=400,
                detail="Cant Delete table it has an active session",
            )

        await self.db.delete(table)

    async def create_resto_table(
            self,
            restaurant: Restaurant,
            payload: list[CreateRestoRequest],
    ) -> list[RestaurantTable]:

        names = [item.table_name.strip().lower() for item in payload]

        # Check duplicates within the request
        if len(names) != len(set(names)):
            raise HTTPException(
                status_code=409,
                detail="Duplicate table names in the request.",
            )

        # Check existing table names in this restaurant
        existing = await self.repo.check_table_name(names, restaurant.id)

        if existing:
            raise HTTPException(
                status_code=409,
                detail="One or more table names already exist.",
            )

        resto_tables = [
            self.model(
                restaurant_id=restaurant.id,
                table_name=item.table_name.strip(),
                capacity=item.capacity,
                is_active=True,
            )
            for item in payload
        ]

        self.db.add_all(resto_tables)

        return resto_tables

    async def update_resto_table(
            self,
            table_id: int,
            payload: CreateRestoRequest,
            restaurant_id: int,
    ) -> RestaurantTable:

        table = await self.repo.get_by_id(table_id, restaurant_id)

        if table is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant table not found",
            )

        table_name = payload.table_name.strip()

        existing = await self.repo.check_table_name(
            [table_name.lower()],
            restaurant_id,
            exclude_id=table_id,
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Table name '{table_name}' already exists.",
            )

        table.table_name = table_name
        table.capacity = payload.capacity
        table.is_active = payload.is_active

        return table

    async def update_table_sesh_status(self, session_token, payload: CreateSeshStatusRequest):
        dinning_sesh = await self.repo.get_dinning_sesh(session_token)

        if dinning_sesh is None:
            raise HTTPException(status_code=404, detail="Dinning session not found")

        dinning_sesh.status = payload.status
        if payload.status == "closed":
            dinning_sesh.is_active = False
            dinning_sesh.closed_at = datetime.now(timezone.utc)


        return dinning_sesh

    async def validate_table_qr_token(self, qr_token:str):
        stmt = (
            select(self.model)
            .options(selectinload(self.model.restaurant))
            .where(self.model.qr_token == qr_token)
        )

        table = await self.db.scalar(stmt)

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

        return table

    async def check_resto_status(self, qr_token: str):

        resto = await self.repo.validate_resto_status(qr_token)

        if resto is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found.",
            )

        config = resto.configuration

        if config.is_24_hours:
            return True

        now = datetime.now(ZoneInfo(resto.country.timezone))

        current_day = now.weekday()
        current_time = now.time()

        previous_day = (current_day - 1) % 7

        today_hours = next(
            (
                hours
                for hours in config.operating_hours
                if hours.day_of_week == current_day
            ),
            None,
        )

        yesterday_hours = next(
            (
                hours
                for hours in config.operating_hours
                if hours.day_of_week == previous_day
            ),
            None,
        )

        is_open = False

        # Check today's schedule.
        if today_hours and not today_hours.is_closed:

            opening = today_hours.opening_time
            closing = today_hours.closing_time

            if opening < closing:
                is_open = opening <= current_time < closing
            else:
                # Overnight schedule.
                is_open = current_time >= opening

        # Check yesterday's overnight schedule.
        if (
                not is_open
                and yesterday_hours
                and not yesterday_hours.is_closed
                and yesterday_hours.opening_time > yesterday_hours.closing_time
        ):
            is_open = current_time < yesterday_hours.closing_time

        return is_open