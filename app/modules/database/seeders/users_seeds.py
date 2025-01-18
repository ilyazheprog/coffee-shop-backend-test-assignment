from modules.dataclasses import Role
from modules.envs.settings import settings

fields = [
    "id",
    "role_id",
    "username",
    "personal_discount_value",
    "personal_discount_type_id",
]

data = [
    [settings.bot.admin_id, Role.ADMIN, settings.bot.admin_username, 100, 1],
    [7658129475, Role.CLIENT, "pimidor4ik", 0, None],
]
