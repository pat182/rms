from datetime import datetime
from typing import Literal


from ...schemas.restaurant.restaurant_schema import RestaurantData
from ...core.base_schema import BaseSchema
from pydantic import ConfigDict


# ==================== REQUEST SCHEMAS ====================

class CreateSeshStatusRequest(BaseSchema):
    status : Literal["pending", "verified", "closed"]

class CreateRestoRequest(BaseSchema):
    table_name: str
    capacity: int
    is_active : bool = True



# ==================== DATA SCHEMAS ====================
class DefaultDinningSession(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
    restaurant_table_id: int
    session_token: str
    is_active: bool = True
    status : Literal["pending", "verified", "closed"]
    started_at: datetime
    closed_at: datetime | None = None

class DiningSessionWithTableData(DefaultDinningSession):
    restaurant_table: "DefaultRestoTable"

class DefaultRestoTable(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
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

class TableWithDinningSessionData(DefaultRestoTable):
    dining_sessions: list[DefaultDinningSession] = []

# ==================== RESPONSE SCHEMAS ====================

class CreateRestoTableResponse(BaseSchema):
    success : bool
    data : list[DefaultRestoTable]


class UpdateRestoTableResponse(BaseSchema):
    success: bool
    data: DefaultRestoTable