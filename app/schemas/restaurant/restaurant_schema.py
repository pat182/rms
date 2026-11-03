from datetime import datetime

from pydantic import EmailStr, ConfigDict

from ...core.base_schema import BaseSchema
from ...schemas.country.country_schema import CountryData


# ==================== REQUEST SCHEMAS ====================
class RestaurantStatusRequest(BaseSchema):
    is_active: bool

class CreateRestaurantRequest(BaseSchema):
    country_id: int
    restaurant_name: str
    contact_number: str
    address: str
    email: EmailStr | None = None


# ==================== DATA SCHEMAS ====================
class RestaurantData(BaseSchema):
    id: int
    country_id: int
    restaurant_name: str
    contact_number: str
    address: str
    email: str | None = None
    is_active: bool
    country: CountryData
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ==================== RESPONSE SCHEMAS ====================
class CreateRestaurantResponse(BaseSchema):
    success: bool
    data: RestaurantData