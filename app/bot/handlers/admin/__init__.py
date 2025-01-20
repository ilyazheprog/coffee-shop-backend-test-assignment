from .admin_panel import router as admin_panel_router
from .menu_items import router as menu_items_router
from .menu_categories import router as menu_categories_router
from .statuses import router as statuses_router
from .delivery_methods import router as delivery_methods_router
from .orders import router as orders_router
from .assign_barista import router as assign_barista_router
from .menu import router as menu_router

__all__ = [
    "admin_panel_router",
    "menu_items_router",
    "menu_categories_router",
    "statuses_router",
    "delivery_methods_router",
    "orders_router",
    "assign_barista_router",
    "menu_router",
]
