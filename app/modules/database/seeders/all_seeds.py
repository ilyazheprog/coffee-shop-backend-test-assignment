from modules.envs import settings

from ..models import Role, User
from .roles_seeds import data as data_roles, fields as fields_roles
from .users_seed import data as data_users, fields as fields_users

all_seeds = [
    (Role, fields_roles, data_roles),
    (User, fields_users, data_users)
]
