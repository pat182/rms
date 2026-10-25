from app.model.country import Country
from app.model.restaurant import Restaurant
from app.schemas.restaurant_schema import CreateRestaurantRequest

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class RestaurantService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.model = Restaurant

    async def get_restaurant(self,restaurant_id):

        result = await self.db.execute(
            select(self.model).where(
                self.model.id == restaurant_id
            )
        )

        restaurant = result.scalar_one_or_none()

        if restaurant is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )

        return restaurant

    async def update_status(self,restaurant_id,is_active: bool):

        restaurant = await self.get_restaurant(restaurant_id)

        restaurant.is_active = is_active

        await self.db.commit()
        await self.db.refresh(restaurant)

        return restaurant

    async def create_restaurant(self,payload: CreateRestaurantRequest):
        country = await self.db.get(Country,payload.country_id)

        if not country:
            raise HTTPException(
                status_code=404,
                detail="Country not found"
            )

        existing = await self.db.execute(
            select(self.model).where(
                self.model.restaurant_name == payload.restaurant_name
            )
        )

        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Restaurant already exists"
            )

        restaurant = self.model(
            country_id=payload.country_id,
            restaurant_name=payload.restaurant_name,
            contact_number=payload.contact_number,
            address=payload.address,
            email=payload.email,
        )

        self.db.add(restaurant)

        await self.db.commit()

        await self.db.refresh(restaurant)

        return restaurant

