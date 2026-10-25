from collections import defaultdict

from app.model.menu import Menu
from app.model.menu_category import MenuCategory
from app.schemas import CreateMenuCategoryRequest

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


class MenuCategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = MenuCategory

    async def create_menu_category(self,menu_id: int,payload: list[CreateMenuCategoryRequest]):

        # Validate menu exists
        menu = await self.db.scalar(
            select(Menu.id).where(Menu.id == menu_id)
        )

        if menu is None:
            raise HTTPException(
                status_code=404,
                detail="Menu not found",
            )

        # Get existing maximum sort order for each parent_id
        result = await self.db.execute(
            select(
                MenuCategory.parent_id,
                func.max(MenuCategory.sort_order),
            )
            .where(MenuCategory.menu_id == menu_id)
            .group_by(MenuCategory.parent_id)
        )
        max_sort_orders = {
            parent_id: max_order for parent_id, max_order in result.all()
        }

        # Prepare top-level categories
        categories = []

        next_category_order = max_sort_orders.get(None)
        next_category_order = (
            next_category_order + 1
            if next_category_order is not None
            else 0
        )

        for category in payload:
            new_category = self.model(
                menu_id=menu_id,
                parent_id=None,
                category_name=category.category_name,
                sort_order=next_category_order,
            )

            categories.append(new_category)
            next_category_order += 1

        # Insert categories and obtain their generated IDs
        self.db.add_all(categories)
        await self.db.flush()

        # Prepare subcategories
        subcategories = []

        for category_data, category_model in zip(payload, categories):
            parent_id = category_model.id

            next_subcategory_order = max_sort_orders.get(parent_id)
            next_subcategory_order = (
                next_subcategory_order + 1
                if next_subcategory_order is not None
                else 0
            )

            for subcategory_data in category_data.subcategories:
                new_subcategory = self.model(
                    menu_id=menu_id,
                    parent_id=parent_id,
                    category_name=subcategory_data.category_name,
                    sort_order=next_subcategory_order,
                )

                subcategories.append(new_subcategory)
                next_subcategory_order += 1

        # Insert all subcategories together
        if subcategories:
            self.db.add_all(subcategories)
            await self.db.flush()

        subcategories_by_parent = defaultdict(list)

        for subcategory in subcategories:
            subcategories_by_parent[subcategory.parent_id].append({
                "id": subcategory.id,
                "menu_id": subcategory.menu_id,
                "parent_id": subcategory.parent_id,
                "category_name": subcategory.category_name,
                "sort_order": subcategory.sort_order,
                "created_at": subcategory.created_at,
                "updated_at": subcategory.updated_at,
            })

        # Build nested categories
        nested_categories = []

        for category in categories:
            nested_categories.append({
                "id": category.id,
                "menu_id": category.menu_id,
                "parent_id": category.parent_id,
                "category_name": category.category_name,
                "sort_order": category.sort_order,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
                "subcategories": subcategories_by_parent[category.id],
            })

        await self.db.commit()

        return nested_categories
