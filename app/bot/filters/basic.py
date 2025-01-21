from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message
import httpx

from modules.dataclasses.roles import Role
from modules.envs.settings import settings


class AdminFilter(BaseFilter):
    """
    Фильтр для проверки, является ли пользователь администратором.
    """

    def __init__(self):
        self.admin_id = settings.bot.admin_id

    async def __call__(self, message: Message) -> bool:
        """
        Проверяет, является ли пользователь администратором.
        """
        return message.from_user.id == self.admin_id


class BaristaFilter(BaseFilter):
    """
    Фильтр для проверки, является ли пользователь бариста.
    """

    async def __call__(self, message: Message) -> bool:
        """
        Проверяет, является ли пользователь бариста.
        """
        tg_id = message.from_user.id
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.bot.backend_url}/users/{tg_id}")

            if response.status_code == 404:
                return False

            if response.status_code == 200:
                user = response.json()
                return user["role_id"] == Role.BARISTA_ID


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
