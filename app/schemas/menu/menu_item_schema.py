from datetime import datetime
from decimal import Decimal
from app.core.base_schema import BaseSchema
from pydantic import ConfigDict,Field,field_validator

class CreateMenuItemRequest(BaseSchema):
    client_id: str | None = None
    menu_category_id: int | None = None
    item_name: str
    description: str | None = None
    price: Decimal
    image_url: str | None = None
    is_available: bool | None = True
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

class MenuItemData(BaseSchema):
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int
    menu_id: int
    menu_category_id: int | None
    item_name: str
    description: str | None
    price: Decimal
    image_url: str | None
    is_available: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

class MenuItemDataWithClientID(MenuItemData):
    client_id: str | None = None

class CreateMenuItemResponse(BaseSchema):
    success: bool
    data: list[MenuItemData]

class MenuItemResponse(BaseSchema):
    success: bool
    data: MenuItemData