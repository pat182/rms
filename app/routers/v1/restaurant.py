from typing import Literal, Optional

from ...dependencies import get_authenticated_user
from ...model import User, Restaurant
from ...schemas import (
    CreateRestaurantRequest,
    CreateRestaurantResponse,
    RestaurantStatusRequest,
    PaginatedResponse,
    RestaurantData
)
from ...services.restaurant.restaurant_service import RestaurantService
from ...model.repositories import RestaurantRepository
from ...core.dependencies import get_db

from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/v1/restaurants",
    tags=["Restaurants"],
    dependencies=[Depends(get_authenticated_user)],
)
@router.get("",response_model=PaginatedResponse[RestaurantData])
async def index(
    page:int=Query(1,ge=1),
    page_size:int=Query(25,ge=1),
    db: AsyncSession = Depends(get_db),
    sort_by: Optional[Literal["restaurant_name", "created_at", "updated_at"]] = Query(None),
    sort_order: Optional[Literal["asc", "desc"]] = Query(None),
    search: Optional[str] = Query(None),

):
    resto_repo = RestaurantRepository(db)

    restaurants, total = await resto_repo.filter(page, page_size, sort_by, sort_order, search,relationships=[
        Restaurant.country,
    ])
    return PaginatedResponse(page=page, page_size=page_size, total_items=total, data=restaurants)


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



