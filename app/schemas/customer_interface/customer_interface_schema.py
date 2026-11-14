import decimal
from decimal import Decimal
from datetime import datetime
from typing import Literal

from ...core.base_schema import BaseSchema
from ..restaurant.restaurant_table_schema import DiningSessionWithTableData

from pydantic import Field, ConfigDict


# ==================== REQUEST SCHEMAS ====================

class JoinRequestApproval(BaseSchema):
    request_token: str
    approved: bool

class OrderStatusRequest(BaseSchema):
    status : Literal["canceled","pending", "preparing", "ready", "served"]
    cancel_reason: str | None = None


class CustomerCartRequest(BaseSchema):
    itemId: int
    itemName: str
    unitPrice: Decimal
    quantity: int = Field(gt=0)
    specialRequest : str = ''

# ==================== DATA SCHEMAS ====================

class OrderItem(BaseSchema):
    id:int
    order_id: int
    menu_item_id: int
    item_name: str
    unit_price:Decimal
    quantity: int
    special_request: str | None
    subtotal: Decimal
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CustomerOrderData(BaseSchema):
    id: int
    restaurant_id: int
    dining_session_token: str
    status: Literal["pending", "preparing", "ready", "served", "canceled"]
    subtotal: Decimal
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)



class CustomerOrderWithItemsAndSession(CustomerOrderData):
    items: list[OrderItem]
    dining_session : DiningSessionWithTableData

class CustomerOrderWithItem(CustomerOrderData):
    items: list[OrderItem]


# ==================== RESPONSE SCHEMAS ====================

class GetOrdersResponse(BaseSchema):
    success: bool
    data: list[CustomerOrderWithItemsAndSession]
class GetOrdersWithItemData(BaseSchema):
    success: bool
    data: list[CustomerOrderWithItem]


