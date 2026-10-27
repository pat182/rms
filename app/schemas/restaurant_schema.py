from datetime import datetime

from app.core.base_schema import BaseSchema
from pydantic import EmailStr

class RestaurantStatusRequest(BaseSchema):
    is_active: bool

class CreateRestaurantRequest(BaseSchema):
    country_id: int
    restaurant_name: str
    contact_number: str
    address: str
    email: EmailStr | None = None

class RestaurantData(BaseSchema):
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

class CreateRestaurantResponse(BaseSchema):
    success: bool
    data: RestaurantData