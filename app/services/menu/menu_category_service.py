from collections import defaultdict

from ...model.menu import Menu
from ...model.menu_category import MenuCategory
from ...schemas import (
    CreateMenuCategoryRequest,
    CreateCompleteMenuCategoryRequest, MenuItemDataWithClientID,UpdateCompleteMenuCategoryRequest,
    MenuCategoryData
)
from ...model.repositories import MenuCategoryRepository,MenuRepository

from .menu_item_service import MenuItemService
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException



class MenuCategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = MenuCategory
        self.repo = MenuCategoryRepository(db)


    async def create_complete_menu_category(
            self,
            menu_id: int,
            payload: list[CreateCompleteMenuCategoryRequest],
            item_service: MenuItemService,
            auth_restaurant_id : int
    ):
        menu_repo = MenuRepository(self.db)
        # 1. Validate that the menu exists
        menu = await menu_repo.get_by_id(menu_id,auth_restaurant_id)
        # menu = await self.db.scalar(
        #     select(Menu.id).where(Menu.id == menu_id)
        # )

        if menu is None:
            raise HTTPException(
                status_code=404,
                detail="Menu not found",
            )

        if not payload:
            return []

        # 2. Get the maximum sort order for each parent
        result = await self.db.execute(
            select(
                self.model.parent_id,
                func.max(self.model.sort_order),
            )
            .where(self.model.menu_id == menu.id)
            .group_by(self.model.parent_id)
        )

        max_sort_orders = dict(result.all())

        # Start at 0 when no records exist; otherwise use max + 1.
        next_sort_orders = {
            parent_id: max_sort_order + 1
            for parent_id, max_sort_order in max_sort_orders.items()
            if max_sort_order is not None
        }

        # 3. Create top-level categories
        categories = []

        for category_data in payload:
            next_sort_order = next_sort_orders.get(None, 0)

            category = self.model(
                menu_id=menu_id,
                parent_id=None,
                category_name=category_data.category_name,
                sort_order=next_sort_order,
            )

            next_sort_orders[None] = next_sort_order + 1

            categories.append(
                (category_data.client_id, category)
            )

        self.db.add_all([
            category
            for _, category in categories
        ])

        await self.db.flush()

        # 4. Collect category items and create subcategories
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
                next_sort_order = next_sort_orders.get(category.id, 0)

                subcategory = self.model(
                    menu_id=menu_id,
                    parent_id=category.id,
                    category_name=subcategory_data.category_name,
                    sort_order=next_sort_order,
                )

                next_sort_orders[category.id] = next_sort_order + 1

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
        # from app.core.logger import log_info
        # log_info("==================================")
        # log_info("MENU:", menu)
        # log_info("==================================")
        if nested_items_payload:
            inserted_items = await item_service.create_menu_items(
                menu_id,
                nested_items_payload,
                auth_restaurant_id
            )

        # Group items by category ID, retaining each item's client_id
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

    async def __upsert_category(
            self,
            menu_id: int,
            category_data,
            parent_id: int | None = None,
    ):
        if category_data.id is not None:
            result = await self.repo.get_model_by_list_id(
                [category_data.id],self.model.menu_id,menu_id
            )
            category = next(iter(result.all()), None)

            if category is None:
                raise ValueError(
                    f"Category {category_data.id} not found in menu {menu_id}"
                )

            if category.parent_id != parent_id:
                raise ValueError(
                    f"Category {category_data.id} does not belong "
                    f"to parent category {parent_id}"
                )

            category.category_name = category_data.category_name
            category.sort_order = category_data.sort_order
        else:
            category = self.model(
                menu_id=menu_id,
                category_name=category_data.category_name,
                sort_order=category_data.sort_order,
                parent_id=parent_id,
            )
            self.db.add(category)

        category.parent_id = parent_id
        category.client_id = category_data.client_id

        await self.db.flush()
        return category

    async def __upsert_category_items(
            self,
            menu_id: int,
            category_id: int,
            items,
            item_service,
    ):
        if not items:
            return []

        return await item_service.upsert_menu_item(
            menu_id=menu_id,
            menu_items=[
                item.model_copy(
                    update={"menu_category_id": category_id}
                )
                for item in items
            ],
        )

    async def upsert_complete_menu_categories(
            self,
            menu_id: int,
            categories: list[UpdateCompleteMenuCategoryRequest],
            item_service: MenuItemService,
    )->list[MenuCategoryData]:
        response_categories = []

        for cat_data in categories:
            # Create/update main category
            category = await self.__upsert_category(
                menu_id=menu_id,
                category_data=cat_data,
                parent_id=None,
            )

            saved_items = await self.__upsert_category_items(
                menu_id=menu_id,
                category_id=category.id,
                items=cat_data.menu_items,
                item_service=item_service,
            )

            response_subcategories = []

            for subcat_data in cat_data.subcategories or []:
                # Create/update subcategory
                subcategory = await self.__upsert_category(
                    menu_id=menu_id,
                    category_data=subcat_data,
                    parent_id=category.id,
                )

                saved_subcategory_items = await self.__upsert_category_items(
                    menu_id=menu_id,
                    category_id=subcategory.id,
                    items=subcat_data.menu_items,
                    item_service=item_service,
                )

                response_subcategories.append({
                    "id": subcategory.id,
                    "client_id": subcategory.client_id,
                    "menu_id": subcategory.menu_id,
                    "category_name": subcategory.category_name,
                    "sort_order": subcategory.sort_order,
                    "parent_id": subcategory.parent_id,
                    "created_at": subcategory.created_at,
                    "updated_at": subcategory.updated_at,
                    "menu_items": saved_subcategory_items,
                })

            response_categories.append({
                "id": category.id,
                "client_id": category.client_id,
                "menu_id": category.menu_id,
                "category_name": category.category_name,
                "sort_order": category.sort_order,
                "parent_id": category.parent_id,
                "created_at": category.created_at,
                "updated_at": category.updated_at,
                "menu_items": saved_items,
                "subcategories": response_subcategories,
            })

        return response_categories

    async def delete_categories(
            self,
            menu_id: int,
            ids: list[int]
    )->None:
        if not ids:
            return
        await self.repo.delete_categories(menu_id, ids)
