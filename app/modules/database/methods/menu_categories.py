from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models import MenuCategory


async def get_all_categories(session: AsyncSession) -> list[MenuCategory]:
    """
    Получает список всех категорий меню.

    :param session: Сессия базы данных.
    :return: Список всех категорий меню.
    """
    result = await session.execute(select(MenuCategory))
    return result.scalars().all()


async def create_category(name: str, session: AsyncSession) -> MenuCategory:
    """
    Создаёт новую категорию меню.

    :param name: Название категории.
    :param session: Сессия базы данных.
    :return: Объект новой категории.
    """
    existing = await session.execute(
        select(MenuCategory).where(MenuCategory.name == name)
    )
    if existing.scalars().first():
        raise ValueError("Категория с таким названием уже существует.")
    category = MenuCategory(name=name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def delete_category(category_id: int, session: AsyncSession) -> None:
    """
    Удаляет категорию меню по ID.

    :param category_id: ID категории.
    :param session: Сессия базы данных.
    :return: None
    """
    category = await session.get(MenuCategory, category_id)
    if not category:
        raise ValueError("Категория не найдена.")
    await session.delete(category)
    await session.commit()
