from ..models import Role, User, DeliveryMethod, OrderStatus, MenuCategory, MenuItem
from .roles_seeds import data as data_roles, fields as fields_roles
from .users_seed import data as data_users, fields as fields_users
from .delivery_methods_seeds import (
    data as data_delivery_methods,
    fields as fields_delivery_methods,
)
from .order_statuses_seeds import (
    data as data_order_statuses,
    fields as fields_order_statuses,
)
from .menu_categories_seed import data as data_categories, fields as fields_categories
from .menu_items_seed import data as data_items, fields as fields_items


all_seeds = [
    (Role, fields_roles, data_roles),
    (User, fields_users, data_users),
    (DeliveryMethod, fields_delivery_methods, data_delivery_methods),
    (OrderStatus, fields_order_statuses, data_order_statuses),
    (MenuCategory, fields_categories, data_categories),
    (MenuItem, fields_items, data_items),
]
