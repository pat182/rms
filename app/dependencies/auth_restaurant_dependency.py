from ..dependencies import get_authenticated_user
from ..model import User, Role

from fastapi import Header, Depends, HTTPException



async def get_current_restaurant(
    restaurant_id: int = Header(..., alias="X-RESTAURANT-ID"),
    auth_user: User = Depends(get_authenticated_user),
):




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

def require_role(*allowed_roles: str):
    async def dependency(
            restaurant_id: int = Header(..., alias="X-RESTAURANT-ID"),
            auth_user=Depends(get_authenticated_user),
    ):

        if auth_user.role.role_name not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions",
            )

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
                detail="Restaurant access denied",
            )



        return restaurant

    return dependency