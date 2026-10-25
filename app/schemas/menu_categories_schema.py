from datetime import datetime

from app.schemas.menu_item_schema import MenuItemData,CreateMenuItemRequest

from pydantic import BaseModel, ConfigDict, Field


class CreateSubcategoryRequest(BaseModel):
    category_name: str
    sort_order: int = 0
    menu_items: list[CreateMenuItemRequest] = []

class CreateMenuCategoryRequest(BaseModel):
    category_name: str
    sort_order: int = 0
    subcategories: list[CreateSubcategoryRequest] = Field(
        default_factory=list
    )

class CreateCompleteMenuCategoryRequest(CreateMenuCategoryRequest):
    menu_items: list[CreateMenuItemRequest] = []

class MenuCategoryDataV2(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
    id : int
    menu_id: int
    parent_id: int | None
    category_name: str
    sort_order : int
    created_at: datetime
    updated_at: datetime
    subcategories: list["MenuSubCategoryData"] = Field(default_factory=list)
    menu_items: list["MenuItemData"] = Field(default_factory=list)

class MenuSubCategoryData(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int
    menu_id: int
    parent_id: int | None
    category_name: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

class CreatedMenuCategoryData(BaseModel):
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

class CreateMenuCategoryResponse(BaseModel):
    success: bool
    data: list[CreatedMenuCategoryData]
