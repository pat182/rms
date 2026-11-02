from .restaurant import router as restaurant_router
from .menu_route import router as menu_router
from .menu_category_route import router as menu_category_router
from .menu_item_route import router as menu_item_router
from .authentication import router as authentication_router
from .restaurant_table_route import router as restaurant_table_router



__all__ = [
    "restaurant_router",
    "menu_router",
    "menu_category_router",
    "menu_item_router",
    "authentication_router",
    "restaurant_table_router"
]
