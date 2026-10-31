from ..dependencies import get_authenticated_user
from ..model import User

from fastapi import Header, Depends, HTTPException


async def get_current_restaurant(
    restaurant_id: int = Header(..., alias="X-RESTAURANT-ID"),
    auth_user: User = Depends(get_authenticated_user),
):
    # from app.core.logger import log_info
    # log_info("========== RESTAURANT DEBUG ==========")
    #
    # for r in auth_user.restaurant_users:
    #     log_info(f"RestaurantUser: {r.__dict__}")
    #
    #     if r.restaurants:
    #         log_info(f"Restaurant: {r.restaurants.__dict__}")
    #
    # log_info("======================================")

    restaurant = next(
        (
            r.restaurants
            for r in auth_user.restaurant_users
            if r.restaurant_id == restaurant_id
        ),
        None,
    )

    if not restaurant:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this restaurant.",
        )

    return restaurant