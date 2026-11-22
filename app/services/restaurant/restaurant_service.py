from datetime import time

from ...model import (User,Restaurant,Country)
from ...model.repositories import RestaurantRepository,RestaurantConfigRepository,RestaurantOpHoursRepository

from app.schemas.restaurant.restaurant_schema import CreateRestaurantRequest

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

class RestaurantService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.repo = RestaurantRepository(self.db)
        self.model = self.repo.model

    async def get_restaurant(self,restaurant_id,auth_user:User):

        result = await self.repo.get_user_restaurant(restaurant_id,auth_user.id)

        restaurant = result.unique().scalar_one_or_none()


        if restaurant is None:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )

        return restaurant

    async def update_status(self,restaurant_id,is_active: bool,auth_user:User):

        restaurant = await self.get_restaurant(restaurant_id,auth_user)


        restaurant.is_active = is_active


        return restaurant

    async def update_restaurant(self,restaurant:Restaurant,payload:CreateRestaurantRequest)-> Restaurant:

        resto = await self.repo.get_resto_by_name(payload.restaurant_name,restaurant.id)

        if resto.scalar_one_or_none() is not None:

            raise HTTPException(
                status_code=409,
                detail=f"{payload.restaurant_name} name already exists",
            )


        restaurant.country_id = 1
        restaurant.restaurant_name = payload.restaurant_name
        restaurant.address = payload.address
        restaurant.contact_number = payload.contact_number
        restaurant.email = payload.email
        restaurant.is_active = payload.is_active
        # config
        resto_config = restaurant.configuration
        resto_config.is_24_hours = payload.configuration.is_24_hours

        for db_day, payload_day in zip(
                resto_config.operating_hours,
                payload.configuration.operating_hours
        ):
            if resto_config.is_24_hours:
                db_day.opening_time = None
                db_day.closing_time = None
                db_day.is_closed = False
            else:
                db_day.opening_time = payload_day.opening_time
                db_day.closing_time = payload_day.closing_time
                db_day.is_closed = payload_day.is_closed

        # from app.core.logger import log_info
        # log_info("===========================================")
        # log_info("RESTAURANT UPDATE")
        # log_info("===========================================")
        
        return restaurant


    async def create_restaurant(self,payload: CreateRestaurantRequest,auth_user:User):
        country = await self.db.get(Country,payload.country_id)

        if not country:
            raise HTTPException(
                status_code=404,
                detail="Country not found"
            )

        existing = await self.repo.get_resto_by_name(payload.restaurant_name)

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

        await self.db.flush()

        resto_config_repo = RestaurantConfigRepository(self.db)

        configuration = resto_config_repo.model(
            restaurant_id=restaurant.id,
            is_24_hours=False,
        )
        self.db.add(configuration)

        await self.db.flush()

        resto_op_repo = RestaurantOpHoursRepository(self.db)
        operating_hours = [
            resto_op_repo.model(
                configuration_id=configuration.id,
                day_of_week=day,
                is_closed=True,
            )
            for day in range(7)
        ]
        self.db.add_all(operating_hours)
        await self.db.flush()

        await self.repo.create_restaurant_user(restaurant.id,auth_user.id)


        return restaurant
