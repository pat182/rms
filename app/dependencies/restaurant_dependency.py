from ..dependencies import get_authenticated_user
from ..model import User

from fastapi import Header, Depends, HTTPException


async def get_current_restaurant(
    restaurant_id: int = Header(..., alias="X-RESTAURANT-ID"),
    auth_user: User = Depends(get_authenticated_user),
):
    restaurant = next(
        (
            restaurant
            for restaurant in auth_user.restaurants
            if restaurant.id == restaurant_id
        ),
        None,
    )

    if not restaurant:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this restaurant.",
        )

    return restaurant