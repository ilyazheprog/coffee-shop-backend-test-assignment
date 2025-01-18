from modules.envs import settings

from ..models import (
    Config,
    DeviceType,
    DiscountType,
    Role,
    Status,
    TransactionType,
    User,
)
from .config_seeds import data as data_configs, fields as fields_configs
from .device_types_seeds import data as data_device_types, fields as fields_device_types
from .discount_types_seeds import (
    data as data_discount_types,
    fields as fields_discount_types,
)
from .roles_seeds import data as data_roles, fields as fields_roles
from .statuses_seeds import data as data_statuses, fields as fields_statuses
from .transaction_types_seeds import (
    data as data_payment_types,
    fields as fields_payment_types,
)
from .users_seeds import data as data_user, fields as fields_user

all_seeds = [
    (DiscountType, fields_discount_types, data_discount_types, True),
    (Role, fields_roles, data_roles, True),
    (DeviceType, fields_device_types, data_device_types, True),
    (User, fields_user, data_user, True),
    (Status, fields_statuses, data_statuses, True),
    (TransactionType, fields_payment_types, data_payment_types, True),
    (Config, fields_configs, data_configs, False),
]

"""
if settings.is_test:
    from ..models import Location, Server, KeyUser
    from .tests.locations_seeds import data as locations_data, fields as locations_fields
    from .tests.servers_seeds import data as servers_data, fields as servers_fields
    from .tests.keys_users_seeds import data as keys_users_data, fields as keys_users_fields

    all_seeds.append((Location, locations_fields, locations_data))
    all_seeds.append((Server, servers_fields, servers_data))
    all_seeds.append((KeyUser, keys_users_fields, keys_users_data))
"""
