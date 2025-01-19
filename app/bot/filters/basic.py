from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import Message
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



class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type