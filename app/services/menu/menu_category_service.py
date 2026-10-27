from collections import defaultdict

from app.model.menu import Menu
from app.model.menu_category import MenuCategory
from app.schemas import CreateMenuCategoryRequest, CreateCompleteMenuCategoryRequest, MenuItemData, \
    MenuItemDataWithClientID
from .menu_item_service import MenuItemService

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
            parent_id: max_order
            for parent_id, max_order in result.all()
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

        # Group subcategories by parent category
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

        return nested_categories

    async def create_complete_menu_category(
            self,
            menu_id: int,
            payload: list[CreateCompleteMenuCategoryRequest],
            item_service: MenuItemService,
    ):
        # 1. Validate that the menu exists
        menu = await self.db.scalar(
            select(Menu.id).where(Menu.id == menu_id)
        )
        if menu is None:
            raise HTTPException(
                status_code=404,
                detail="Menu not found",
            )

        if not payload:
            return []

        # 2. Get existing maximum sort order for each parent
        result = await self.db.execute(
            select(
                MenuCategory.parent_id,
                func.max(MenuCategory.sort_order),
            )
            .where(MenuCategory.menu_id == menu_id)
            .group_by(MenuCategory.parent_id)
        )

        max_sort_orders = dict(result.all())

        # 3. Create top-level categories, retaining their client_id
        categories = []

        for category_data in payload:
            category = self.model(
                menu_id=menu_id,
                parent_id=None,
                category_name=category_data.category_name,
                sort_order=category_data.sort_order,
            )

            categories.append(
                (category_data.client_id, category)
            )

        self.db.add_all([
            category
            for _, category in categories
        ])

        await self.db.flush()

        # 4. Collect items and create subcategories
        nested_items_payload = []
        subcategories = []
        subcategory_payloads = []

        for category_data, (_, category) in zip(payload, categories):
            # Items directly under the top-level category
            nested_items_payload.extend(
                item.model_copy(
                    update={"menu_category_id": category.id}
                )
                for item in category_data.menu_items
            )

            # Create subcategories and preserve their client_id
            for subcategory_data in category_data.subcategories:
                subcategory = self.model(
                    menu_id=menu_id,
                    parent_id=category.id,
                    category_name=subcategory_data.category_name,
                    sort_order=subcategory_data.sort_order,
                )

                subcategories.append(
                    (subcategory_data.client_id, subcategory)
                )
                subcategory_payloads.append(subcategory_data)

        if subcategories:
            self.db.add_all([
                subcategory
                for _, subcategory in subcategories
            ])

            await self.db.flush()

        # 5. Collect items belonging to subcategories
        for subcategory_data, (_, subcategory) in zip(
                subcategory_payloads,
                subcategories,
        ):
            nested_items_payload.extend(
                item.model_copy(
                    update={"menu_category_id": subcategory.id}
                )
                for item in subcategory_data.menu_items
            )

        # 6. Insert all category/subcategory items in one service call
        inserted_items = []

        if nested_items_payload:
            inserted_items = await item_service.create_menu_item(
                menu_id,
                nested_items_payload,
            )

        # Group items by their category ID, retaining each item's client_id
        items_by_category = defaultdict(list)

        for item in inserted_items:
            items_by_category[item["menu_category_id"]].append(
                MenuItemDataWithClientID.model_validate(item).model_dump(
                    mode="json"
                )
            )

        # 7. Group subcategories under their parent categories
        subcategories_by_parent = defaultdict(list)

        for client_id, subcategory in subcategories:
            subcategories_by_parent[subcategory.parent_id].append({
                "id": subcategory.id,
                "client_id": client_id,
                "menu_id": subcategory.menu_id,
                "parent_id": subcategory.parent_id,
                "category_name": subcategory.category_name,
                "sort_order": subcategory.sort_order,
                "created_at": subcategory.created_at,
                "updated_at": subcategory.updated_at,
                "menu_items": items_by_category[subcategory.id],
            })

        # 8. Build the final nested category response
        return [
            {
                "id": category.id,
                "client_id": client_id,
                "menu_id": category.menu_id,
                "parent_id": category.parent_id,
                "category_name": category.category_name,
                "sort_order": category.sort_order,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
                "menu_items": items_by_category[category.id],
                "subcategories": subcategories_by_parent[category.id],
            }
            for client_id, category in categories
        ]