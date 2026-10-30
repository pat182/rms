from ...dependencies import get_authenticated_user
from ...model import User
from ...schemas import (CreateRestaurantRequest,CreateRestaurantResponse,RestaurantStatusRequest)
from ...services.restaurant.restaurant_service import RestaurantService
from ...core.dependencies import get_db

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/v1/restaurants",
    tags=["Restaurants"],
    dependencies=[Depends(get_authenticated_user)],
)

@router.get("/{restaurant_id}",response_model=CreateRestaurantResponse)
async def show(
        restaurant_id: int,
        auth_user: User = Depends(get_authenticated_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        restaurant_service = RestaurantService(db)
        restaurant = await restaurant_service.get_restaurant(restaurant_id,auth_user)

        return {
            "success": True,
            "data": restaurant
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get restaurant")



@router.put("/{restaurant_id}/status",response_model=CreateRestaurantResponse)
async def toggle_status(
    restaurant_id: int,
    payload: RestaurantStatusRequest,
    auth_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        restaurant_service = RestaurantService(db)
        restaurant = await restaurant_service.update_status(restaurant_id, payload.is_active, auth_user)
        await db.commit()
        return {
            "success": True,
            "data": restaurant
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update status")




@router.post("", response_model=CreateRestaurantResponse)
async def create_restaurant(
        payload: CreateRestaurantRequest,
        auth_user: User = Depends(get_authenticated_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        restaurant_service = RestaurantService(db)
        new_restaurant = await restaurant_service.create_restaurant(payload,auth_user)
        await db.commit()
        return {
            "success": True,
            "data": new_restaurant
        }
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create restaurant")



