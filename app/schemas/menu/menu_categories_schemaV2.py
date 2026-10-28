
from datetime import datetime

from app.schemas.menu.menu_item_schema_v2 import UpdateCompleteMenuItemRequest
from app.core.base_schema import BaseSchema
from pydantic import ConfigDict, Field,field_validator

# ==================== REQUEST SCHEMAS ====================

class UpdateCompleteSubcategoryRequest(BaseSchema):
    id : int | None = None
    category_name: str
    sort_order: int = 0
    client_id: str | None = None
    menu_items: list[UpdateCompleteMenuItemRequest] = Field(default_factory=list)

    @field_validator("category_name")
    @classmethod
    def validate_menu_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Subcategory name is required.")
        return value

class UpdateCompleteMenuCategoryRequest(BaseSchema):
    id: int | None = None
    category_name: str
    sort_order: int = 0
    client_id: str | None = None
    subcategories: list[UpdateCompleteSubcategoryRequest] = Field(
        default_factory=list
    )
    menu_items: list[UpdateCompleteMenuItemRequest] = []

    @field_validator("category_name")
    @classmethod
    def validate_menu_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Category name is required.")
        return value
