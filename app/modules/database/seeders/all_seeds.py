from modules.envs import settings

from ..models import Role
from .roles_seeds import data as data_roles, fields as fields_roles

all_seeds = [
    (Role, fields_roles, data_roles),
]
