from decimal import Decimal

from ...core.base_schema import BaseSchema

from pydantic import Field


class CustomerCartRequest(BaseSchema):
    itemId: int
    itemName: str
    unitPrice: Decimal
    quantity: int = Field(gt=0)
    specialRequest : str = ''

