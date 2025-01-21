from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
import httpx

from bot.handlers.routers import client_router
from bot.keyboards import client_main_menu_kb
from bot.states import ClientStates
from modules.dataclasses.roles import Role
from modules.envs import settings

router = Router()
client_router.include_router(router)

BACKEND_URL = settings.bot.backend_url


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    """Стартовое сообщение для клиента."""
    await state.set_state(ClientStates.main_menu)
    await message.reply(
        "Добро пожаловать в наше заведение!\n", reply_markup=client_main_menu_kb
    )

    user_id = message.from_user.id
    is_registered = True

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/users/{user_id}")
        if response.status_code == 404:
            is_registered = False

    if not is_registered:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/users/",
                json={
                    "tg_id": user_id,
                    "username": message.from_user.username,
                    "role_id": Role.CLIENT_ID,
                },
            )
