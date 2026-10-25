from typing import Optional
from datetime import datetime

from app.schemas.restaurant_schema import RestaurantData
from app.schemas.role_schema import RoleData

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: int
    role_id : int
    email: str
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime
    role : RoleData
    restaurants: list[RestaurantData] = []
    model_config = ConfigDict(from_attributes=True)

class UsersResponseV2(BaseModel):
    id: int
    role_id: int
    email: str
    first_name: str
    last_name: str
    email: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserHttpResponse(BaseModel):
    success: bool
    data: UsersResponseV2