
from datetime import datetime

from pydantic import ConfigDict, Field, field_validator
from app.core.base_schema import BaseSchema

from app.schemas.menu.menu_categories_schema import (
    MenuCategoryData,
    CreateCompleteMenuCategoryRequest,
)
from app.schemas.menu.menu_item_schema import (
    MenuItemData,
    MenuItemDataWithClientID,
    CreateMenuItemRequest,
)


# ==================== REQUEST SCHEMAS ====================

class CreateMenuRequest(BaseSchema):
    menu_name: str
    description: str | None = None
    is_active: bool = False

    @field_validator("menu_name")
    @classmethod
    def validate_menu_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Menu name is required.")
        return value


class CreateCompleteMenuRequest(CreateMenuRequest):
    categories: list[CreateCompleteMenuCategoryRequest] = Field(
        default_factory=list
    )
    menu_items: list[CreateMenuItemRequest] = Field(
        default_factory=list
    )


class UpdateMenuStatusRequest(BaseSchema):
    is_active: bool


# ==================== DATA SCHEMAS ====================

class MenuData(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
    restaurant_id: int
    menu_name: str
    description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MenuDataWithRelationship(MenuData):
    categories: list[MenuCategoryData] = Field(
        default_factory=list
    )
    menu_items: list[MenuItemData] = Field(
        default_factory=list
    )


class CompleteMenuData(MenuDataWithRelationship):
    menu_items: list[MenuItemDataWithClientID] = Field(
        default_factory=list
    )


class ModifiedCompleteMenuData(CompleteMenuData):
    removed_image: list[str] = Field(
        default_factory=list
    )
# ==================== RESPONSE SCHEMAS ====================

class MenuResponse(BaseSchema):
    success: bool
    data: MenuDataWithRelationship


class CreateMenuResponse(BaseSchema):
    success: bool
    data: MenuData


class CreateCompleteMenuResponse(BaseSchema):
    success: bool
    data: CompleteMenuData
