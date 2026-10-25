from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

class CreateMenuItemRequest(BaseModel):
    menu_id: int
    menu_category_id: int | None = None
    is_active: bool = False
    item_name: str
    description: str | None = None
    price: Decimal
    image_url: str | None = None
    is_available: bool = True
    sort_order: int | None = None

class MenuItemData(BaseModel):
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


class CreateMenuItemResponse(BaseModel):
    success: bool
    data: MenuItemData