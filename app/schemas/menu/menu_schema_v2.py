
from datetime import datetime

from pydantic import ConfigDict, Field, field_validator
from app.core.base_schema import BaseSchema

from app.schemas.menu.menu_categories_schemaV2 import (
    UpdateCompleteMenuCategoryRequest
)
from app.schemas.menu.menu_item_schema_v2 import (
    UpdateCompleteMenuItemRequest
)


# ==================== REQUEST SCHEMAS ====================
class RemovedItemsRequestSchema(BaseSchema):
    category_ids: list[int] = Field(default_factory=list)
    category_menu_item_ids: list[int] = Field(default_factory=list)
    menu_item_ids: list[int] = Field(default_factory=list)
    subcategory_ids: list[int] = Field(default_factory=list)
    subcategory_menu_item_ids: list[int] = Field(default_factory=list)

class UpdateCompleteMenuRequest(BaseSchema):
    menu_name: str
    description: str
    is_active: bool = False
    categories: list[UpdateCompleteMenuCategoryRequest] = Field(
        default_factory=list
    )
    menu_items: list[UpdateCompleteMenuItemRequest] = Field(
        default_factory=list
    )

    removed_items: RemovedItemsRequestSchema = Field(
        default_factory=RemovedItemsRequestSchema
    )
    @field_validator("menu_name")
    @classmethod
    def validate_menu_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Menu name is required.")
        return value



# ==================== DATA SCHEMAS ====================




# ==================== RESPONSE SCHEMAS ====================


