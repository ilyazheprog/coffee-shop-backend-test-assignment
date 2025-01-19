from datetime import datetime
from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from ..connect import async_session
from ..models import User


async def add_user(
    tg_id: int,
    role_id: int,
    username: str = None,
):
    """
    Добавляет нового пользователя в базу данных.

    :param tg_id: Telegram ID пользователя.
    :param role_id: ID роли пользователя.
    :param username: Имя пользователя (уникальное).
    :return: Объект нового пользователя.
    """
    async with async_session() as session:
        # Проверяем уникальность имени пользователя
        if username:
            existing_user = await session.execute(
                select(User).where(User.username == username)
            )
            if existing_user.scalars().first():
                raise ValueError("Имя пользователя уже занято.")

        new_user = User(
            id=tg_id,
            role_id=role_id,
            username=username,
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user


async def is_user_exists(tg_id: int) -> bool:
    """
    Проверяет, существует ли пользователь с данным Telegram ID.

    :param tg_id: Telegram ID пользователя.
    :return: True, если пользователь существует, иначе False.
    """
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == tg_id))
        return result.scalars().first() is not None


async def update_role(tg_id: int, new_role_id: int):
    """
    Обновляет роль пользователя.

    :param tg_id: Telegram ID пользователя.
    :param new_role_id: ID новой роли.
    :return: Объект пользователя с обновленной ролью.
    """
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == tg_id))
        user = result.scalars().first()

        if user:
            user.role_id = new_role_id
            await session.commit()
            await session.refresh(user)

        return user


async def update_username(tg_id: int, new_username: str):
    """
    Обновляет имя пользователя.

    :param tg_id: Telegram ID пользователя.
    :param new_username: Новое имя пользователя.
    :return: Объект пользователя с обновленным именем.
    """
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == tg_id))
        user = result.scalars().first()

        if user:
            # Проверяем уникальность нового имени пользователя
            existing_user = await session.execute(
                select(User).where(User.username == new_username)
            )
            if existing_user.scalars().first():
                raise ValueError("Имя пользователя уже занято.")

            user.username = new_username
            await session.commit()
            await session.refresh(user)

        return user


async def get_user_by_tg_id(tg_id: int) -> dict:
    """
    Получает пользователя по Telegram ID вместе с информацией о типе скидки.

    :param tg_id: Telegram ID пользователя.
    :return: Словарь с информацией о пользователе и типе скидки, если найден, иначе None.
    """
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .options(
                joinedload(User.role), joinedload(User.personal_discount_type)
            )  # Загрузка роли и типа скидки
            .where(User.id == tg_id)
        )
        user = result.scalars().first()

        if user:
            return {
                "tg_id": user.id,
                "username": user.username,
                "role_id": user.role_id,
            }
        return None


async def get_all_users() -> list[User]:
    """
    Получает всех пользователей.

    :return: Список всех пользователей.
    """
    async with async_session() as session:
        result = await session.execute(select(User))
        return result.scalars().all()
