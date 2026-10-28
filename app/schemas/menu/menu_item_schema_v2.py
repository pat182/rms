from datetime import datetime
from decimal import Decimal
from app.core.base_schema import BaseSchema
from pydantic import ConfigDict,Field,field_validator

# ==================== REQUEST SCHEMAS ====================


class UpdateCompleteMenuItemRequest(BaseSchema):
    id: int | None
    client_id: str | None = None
    menu_category_id: int | None = None
    item_name: str
    description: str | None = None
    price: Decimal
    image_url: str | None = None
    is_available: bool = True
    sort_order: int | None = None

    @field_validator("item_name")
    @classmethod
    def validate_menu_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("item name is required.")
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("Price should be greater than 0.")
        return value