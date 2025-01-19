from modules.dataclasses import Role
from modules.envs import settings

fields = [
    "id",
    "role_id",
    "username",
]

data = [[settings.bot.admin_id, Role.ADMIN_ID, settings.bot.admin_username]]
