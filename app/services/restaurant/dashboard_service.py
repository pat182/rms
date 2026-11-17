# import datetime
from datetime import time,datetime
from typing import Optional, Literal

from sqlalchemy.orm import selectinload

from ...model import (DiningSession, Restaurant)
from ...model.repositories import RestaurantRepository, RestaurantConfigRepository, RestaurantOpHoursRepository, CustomerOrderRepo

from app.schemas.restaurant.restaurant_schema import CreateRestaurantRequest

from fastapi import HTTPException,Request

from sqlalchemy.ext.asyncio import AsyncSession

class DashboardService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.order_repo = CustomerOrderRepo(self.db)


    async def get_recent_order_data(self,
        restaurant_id:int,
        page:int,
        page_size:int,
        sort_by:Optional[Literal["created_at"]],
        sort_order: Optional[Literal["asc", "desc"]],
        search: Optional[str] = None,
        order_from: datetime | None = None,
        order_at: datetime | None = None,
    ):

        filters = []

        if order_from:
            filters.append(
                self.order_repo.model.created_at >= order_from
            )

        if order_at:
            filters.append(
                self.order_repo.model.created_at <= order_at
            )

        orders, total = await self.order_repo.filter(
            page,
            page_size,
            sort_by,
            sort_order,
            search,
            restaurant_id=restaurant_id,
            relationships=[
                selectinload(self.order_repo.model.items),
                selectinload(self.order_repo.model.dining_session).selectinload(
                    DiningSession.restaurant_table
                ),
            ],
            filters=filters,
        )

        return  orders, total

    async def get_chart_data(
            self,
            restaurant: Restaurant,
            order_from: datetime | None = None,
            order_at: datetime | None = None,
    ):
        configuration = restaurant.configuration

        hourly_counts = await self.order_repo.get_hourly_order_counts(
            restaurant_id=restaurant.id,
            order_from=order_from,
            order_at=order_at,
        )

        total_orders = sum(hourly_counts.values())

        if configuration.is_24_hours:
            operating_hours = {
                "opens_at": "00:00",
                "closes_at": "00:00",
                "is_24_hours": True,
            }
            start_hour, end_hour = 0, 24

        else:
            today = datetime.now().weekday()
            today_hours = next(
                (
                    hours
                    for hours in configuration.operating_hours
                    if hours.day_of_week == today
                ),
                None,
            )

            if (
                    today_hours is None
                    or today_hours.is_closed
                    or today_hours.opening_time is None
                    or today_hours.closing_time is None
            ):
                operating_hours = {
                    "opens_at": None,
                    "closes_at": None,
                    "is_24_hours": False,
                }
                start_hour, end_hour = 0, 0

            else:
                opening_time = today_hours.opening_time
                closing_time = today_hours.closing_time

                operating_hours = {
                    "opens_at": opening_time.strftime("%H:%M"),
                    "closes_at": closing_time.strftime("%H:%M"),
                    "is_24_hours": False,
                }

                start_hour = opening_time.hour
                end_hour = closing_time.hour

                # Support overnight operating hours
                if closing_time <= opening_time:
                    end_hour += 24

        # Generate chart intervals
        chart = [
            {
                "time": datetime.strptime(
                    f"{hour % 24:02d}:00", "%H:%M"
                ).strftime("%I %p").lstrip("0"),
                "orders": hourly_counts.get(hour % 24, 0),
            }
            for hour in range(start_hour, end_hour)
        ]

        return {
            "total_orders": total_orders,
            "operating_hours": operating_hours,
            "interval": "hour",
            "chart": chart,
        }









