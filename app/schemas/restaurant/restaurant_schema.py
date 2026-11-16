from datetime import datetime,time

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
    is_active :  bool = False
    email: EmailStr


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

class RestaurantDataWithOutCountry(BaseSchema):
    id: int
    country_id: int
    restaurant_name: str
    contact_number: str
    address: str
    email: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RestaurantOperatingHoursData(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    configuration_id: int
    day_of_week: int
    opening_time: time | None
    closing_time: time | None
    is_closed: bool


class RestaurantConfigurationData(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int
    is_24_hours: bool
    created_at: datetime
    updated_at: datetime
    operating_hours: list[RestaurantOperatingHoursData]

class RestaurantDataComplete(RestaurantDataWithOutCountry):
    country: CountryData
    configuration: RestaurantConfigurationData | None = None



# ==================== RESPONSE SCHEMAS ====================
class CreateRestaurantResponse(BaseSchema):
    success: bool
    data: RestaurantData

class UpdateRestaurantResponse(BaseSchema):
    success: bool
    data: RestaurantDataWithOutCountry

class CompleteRestaurantResponse(BaseSchema):
    success: bool
    data: RestaurantDataComplete