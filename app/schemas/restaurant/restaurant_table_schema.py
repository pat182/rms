from datetime import datetime
from pydantic import ConfigDict

from ...schemas.restaurant.restaurant_schema import RestaurantData
from ...core.base_schema import BaseSchema
from ...model import Restaurant


# ==================== REQUEST SCHEMAS ====================
class CreateRestoRequest(BaseSchema):
    table_name: str
    capacity: int
    is_active : bool = True

# ==================== DATA SCHEMAS ====================
class DefaultRestoTable(BaseSchema):
    id: int
    restaurant_id: int
    table_name: str
    capacity: int
    is_active: bool = True
    qr_token: str
    created_at: datetime
    updated_at: datetime


class TableWithRestoData(BaseSchema):
    restaurant: RestaurantData

# ==================== RESPONSE SCHEMAS ====================

class CreateRestoTableResponse(BaseSchema):
    success : bool
    data : list[DefaultRestoTable]