from decimal import Decimal
from datetime import datetime
from typing import Literal

from ...core.base_schema import BaseSchema

from pydantic import Field, ConfigDict


class CustomerCartRequest(BaseSchema):
    itemId: int
    itemName: str
    unitPrice: Decimal
    quantity: int = Field(gt=0)
    specialRequest : str = ''


class CustomerOrderData(BaseSchema):
    id: int
    restaurant_id: int
    dining_session_token: str
    status: Literal["pending", "preparing", "ready", "served", "canceled"]
    subtotal: Decimal
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)



