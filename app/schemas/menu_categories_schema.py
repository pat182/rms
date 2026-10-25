from datetime import datetime

from sqlalchemy.util.queue import Empty

from app.schemas.menu_item_schema import MenuItemData

from pydantic import BaseModel, ConfigDict, Field


class CreateSubcategoryRequest(BaseModel):
    category_name: str
    sort_order: int = 0


class CreateMenuCategoryRequest(BaseModel):
    category_name: str
    sort_order: int = 0
    subcategories: list[CreateSubcategoryRequest] = Field(
        default_factory=list
    )

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
    subcategories: list["MenuCategoryDataV2"] = Field(default_factory=list)
    menu_items: list["MenuItemData"] = Field(default_factory=list)

class MenuCategoryData(BaseModel):
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
    subcategories: list[MenuCategoryData] = Field(
        default_factory=list
    )

class CreateMenuCategoryResponse(BaseModel):
    success: bool
    data: list[CreatedMenuCategoryData]
