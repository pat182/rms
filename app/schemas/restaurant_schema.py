from datetime import datetime

from pydantic import BaseModel, EmailStr

class RestaurantStatusRequest(BaseModel):
    is_active: bool

class CreateRestaurantRequest(BaseModel):
    country_id: int
    restaurant_name: str
    contact_number: str
    address: str
    email: EmailStr | None = None

class RestaurantData(BaseModel):
    id: int
    country_id: int
    restaurant_name: str
    contact_number: str
    address: str
    email: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = {
        "from_attributes": True
    }

class CreateRestaurantResponse(BaseModel):
    success: bool
    data: RestaurantData