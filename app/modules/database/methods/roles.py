from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from ..models import Role, User


async def add_role(name: str, session: AsyncSession) -> Role:
    """
    Добавляет новую роль в базу данных.

    :param name: Имя роли (уникальное).
    :param session: Сессия базы данных.
    :return: Объект новой роли.
    """
    existing_role = await session.execute(select(Role).where(Role.name == name))
    if existing_role.scalars().first():
        raise ValueError("Роль с таким именем уже существует.")
    new_role = Role(name=name)
    session.add(new_role)
    await session.commit()
    await session.refresh(new_role)
    return new_role


async def is_role_exists(role_id: int, session: AsyncSession) -> bool:
    """
    Проверяет, существует ли роль с данным ID.

    :param role_id: ID роли.
    :param session: Сессия базы данных.
    :return: True, если роль существует, иначе False.
    """
    result = await session.execute(select(Role).where(Role.id == role_id))
    return result.scalars().first() is not None


async def update_role_name(
    role_id: int, new_name: str, session: AsyncSession
) -> Role | None:
    """
    Обновляет имя роли.

    :param role_id: ID роли.
    :param new_name: Новое имя роли.
    :param session: Сессия базы данных.
    :return: Объект роли с обновленным именем, если найден, иначе None.
    """
    result = await session.execute(select(Role).where(Role.id == role_id))
    role = result.scalars().first()
    if role:
        existing_role = await session.execute(select(Role).where(Role.name == new_name))
        if existing_role.scalars().first():
            raise ValueError("Роль с таким именем уже существует.")
        role.name = new_name
        await session.commit()
        await session.refresh(role)
    return role


async def get_role_by_id(role_id: int, session: AsyncSession) -> Role | None:
    """
    Получает роль по ID.

    :param role_id: ID роли.
    :param session: Сессия базы данных.
    :return: Объект роли, если найден, иначе None.
    """
    result = await session.execute(select(Role).where(Role.id == role_id))
    return result.scalars().first()


async def get_all_roles(session: AsyncSession) -> list[Role]:
    """
    Получает все роли.

    :param session: Сессия базы данных.
    :return: Список всех ролей.
    """
    result = await session.execute(select(Role))
    return result.scalars().all()


async def get_users_by_role_id(role_id: int, session: AsyncSession) -> list[User]:
    """
    Получает всех пользователей с данной ролью.

    :param role_id: ID роли.
    :param session: Сессия базы данных.
    :return: Список пользователей с данной ролью.
    """
    result = await session.execute(
        select(User).options(joinedload(User.role)).where(User.role_id == role_id)
    )
    return [user.id for user in result.scalars().all()]


async def delete_role(role_id: int, session: AsyncSession) -> bool:
    """
    Удаляет роль по ID.

    :param role_id: ID роли.
    :param session: Сессия базы данных.
    :return: True, если удалена, иначе False.
    """
    result = await session.execute(select(Role).where(Role.id == role_id))
    role = result.scalars().first()

    if not role:
        return False

    await session.delete(role)
    await session.commit()
    return True
