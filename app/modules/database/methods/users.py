from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from ..models import User


async def add_user(
    tg_id: int,
    role_id: int,
    username: str,
    session: AsyncSession,
) -> User:
    """
    Добавляет нового пользователя в базу данных.

    :param tg_id: Telegram ID пользователя.
    :param role_id: ID роли пользователя.
    :param username: Имя пользователя (уникальное).
    :param session: Сессия базы данных.
    :return: Объект нового пользователя.
    """
    if username:
        existing_user = await session.execute(
            select(User).where(User.username == username)
        )
        if existing_user.scalars().first():
            raise ValueError("Имя пользователя уже занято.")

    new_user = User(id=tg_id, role_id=role_id, username=username)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def is_user_exists(tg_id: int, session: AsyncSession) -> bool:
    """
    Проверяет, существует ли пользователь с данным Telegram ID.

    :param tg_id: Telegram ID пользователя.
    :param session: Сессия базы данных.
    :return: True, если пользователь существует, иначе False.
    """
    result = await session.execute(select(User).where(User.id == tg_id))
    return result.scalars().first() is not None


async def update_username(
    tg_id: int, new_username: str, session: AsyncSession
) -> User | None:
    """
    Обновляет имя пользователя.

    :param tg_id: Telegram ID пользователя.
    :param new_username: Новое имя пользователя.
    :param session: Сессия базы данных.
    :return: Объект пользователя с обновленным именем, если найден, иначе None.
    """
    result = await session.execute(select(User).where(User.id == tg_id))
    user = result.scalars().first()

    if not user:
        return None

    existing_user = await session.execute(
        select(User).where(User.username == new_username)
    )
    if existing_user.scalars().first():
        raise ValueError("Имя пользователя уже занято.")

    user.username = new_username
    await session.commit()
    await session.refresh(user)
    return user


async def change_user_role(
    tg_id: int, new_role_id: int, session: AsyncSession
) -> User | None:
    """
    Смена роли пользователя.

    :param tg_id: Telegram ID пользователя.
    :param new_role_id: ID новой роли.
    :param session: Сессия базы данных.
    :return: Объект пользователя с обновленной ролью, если найден, иначе None.
    """
    result = await session.execute(select(User).where(User.id == tg_id))
    user = result.scalars().first()

    if not user:
        return None

    user.role_id = new_role_id
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_tg_id(tg_id: int, session: AsyncSession) -> User | None:
    """
    Получает пользователя по Telegram ID.

    :param tg_id: Telegram ID пользователя.
    :param session: Сессия базы данных.
    :return: Объект пользователя, если найден, иначе None.
    """
    result = await session.execute(
        select(User).options(joinedload(User.role)).where(User.id == tg_id)
    )
    return result.scalars().first()


async def get_all_users(session: AsyncSession) -> list[User]:
    """
    Получает всех пользователей.

    :param session: Сессия базы данных.
    :return: Список всех пользователей.
    """
    result = await session.execute(select(User))
    return result.scalars().all()
