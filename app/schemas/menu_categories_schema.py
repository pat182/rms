from datetime import datetime

from app.schemas.menu_item_schema import MenuItemData,CreateMenuItemRequest,MenuItemDataWithClientID
from app.core.base_schema import BaseSchema
from pydantic import ConfigDict, Field,field_validator


class CreateSubcategoryRequest(BaseSchema):
    category_name: str
    sort_order: int = 0
    client_id: str | None = None
    subcategories: list[CreateSubcategoryRequest] = Field(default_factory=list)
    menu_items: list[CreateMenuItemRequest] = Field(default_factory=list)

    @field_validator("category_name")
    @classmethod
    def validate_menu_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Subcategory name is required.")
        return value

class CreateMenuCategoryRequest(BaseSchema):
    category_name: str
    sort_order: int = 0
    client_id: str | None = None
    subcategories: list[CreateSubcategoryRequest] = Field(
        default_factory=list
    )

    @field_validator("category_name")
    @classmethod
    def validate_menu_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Category name is required.")
        return value

class CreateCompleteMenuCategoryRequest(CreateMenuCategoryRequest):
    menu_items: list[CreateMenuItemRequest] = []

class MenuCategoryData(BaseSchema):
    model_config = ConfigDict(
        from_attributes=True
    )
    id : int
    client_id: str | None = None
    menu_id: int
    parent_id: int | None
    category_name: str
    sort_order : int
    created_at: datetime
    updated_at: datetime
    subcategories: list["CompeteMenuSubCategoryData"] = Field(default_factory=list)
    menu_items: list["MenuItemDataWithClientID"] = Field(default_factory=list)

class MenuSubCategoryData(BaseSchema):
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int
    client_id: str | None = None
    menu_id: int
    parent_id: int | None
    category_name: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

class CompeteMenuSubCategoryData(MenuSubCategoryData):
    model_config = ConfigDict(
        from_attributes=True
    )
    menu_items: list["MenuItemDataWithClientID"] = Field(default_factory=list)

class CreatedMenuCategoryData(BaseSchema):
    id: int
    menu_id: int
    parent_id: int | None
    category_name: str
    sort_order: int
    created_at: datetime
    updated_at: datetime
    subcategories: list[MenuSubCategoryData] = Field(
        default_factory=list
    )

class CreateMenuCategoryResponse(BaseSchema):
    success: bool
    data: list[CreatedMenuCategoryData]
