from datetime import datetime

from app.schemas.menu_categories_schema import MenuCategoryDataV2
from app.schemas.menu_item_schema import MenuItemData

from pydantic import BaseModel,ConfigDict,Field

class CreateMenuRequest(BaseModel):
    menu_name: str
    description: str | None = None
    is_active: bool = False

class MenuDataV2(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int
    restaurant_id: int
    menu_name: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    categories: list[MenuCategoryDataV2] = Field(
        default_factory=list
    )

    menu_items: list[MenuItemData] = Field(
        default_factory=list
    )

class MenuData(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int
    restaurant_id: int
    menu_name: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class MenuResponse(BaseModel):
    success: bool
    data: MenuDataV2

class CreateMenuResponse(BaseModel):
    success: bool
    data: MenuData