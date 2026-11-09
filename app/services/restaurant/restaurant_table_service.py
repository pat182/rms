# from sentry_sdk.utils import now
from datetime import datetime, timezone

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
            self,restaurant: Restaurant,
            payload:list[CreateRestoRequest],
    )-> list[RestaurantTable]:

        resto_tables : list[RestaurantTable] = []

        for resto in payload:

            resto_table = self.model(
                restaurant_id=restaurant.id,
                table_name=resto.table_name,
                capacity=resto.capacity,
                is_active=True
            )
            resto_tables.append(resto_table)

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

        table.table_name = payload.table_name
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