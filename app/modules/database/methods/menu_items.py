from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import MenuItem


async def get_all_menu_items(session: AsyncSession) -> list[MenuItem]:
    """
    Возвращает список всех позиций меню.
    """
    result = await session.execute(select(MenuItem))
    return result.scalars().all()


async def get_menu_item_by_id(item_id: int, session: AsyncSession) -> MenuItem | None:
    """
    Возвращает позицию меню по её ID.
    """
    return await session.get(MenuItem, item_id)


async def create_menu_item(
    name: str, category_id: int, weight: float, price: float, is_available: bool, session: AsyncSession
) -> MenuItem:
    """
    Создаёт новую позицию в меню.
    """
    item = MenuItem(
        name=name,
        category_id=category_id,
        weight=weight,
        price=price,
        is_available=is_available
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def update_menu_item(
    item_id: int, name: str | None, category_id: int | None, weight: float | None,
    price: float | None, is_available: bool | None, session: AsyncSession
) -> MenuItem | None:
    """
    Обновляет данные позиции меню.
    """
    item = await session.get(MenuItem, item_id)
    if not item:
        return None

    if name is not None:
        item.name = name
    if category_id is not None:
        item.category_id = category_id
    if weight is not None:
        item.weight = weight
    if price is not None:
        item.price = price
    if is_available is not None:
        item.is_available = is_available

    await session.commit()
    await session.refresh(item)
    return item


async def update_menu_item_availability(item_id: int, is_available: bool, session: AsyncSession) -> MenuItem | None:
    """
    Обновляет доступность позиции меню.
    """
    item = await session.get(MenuItem, item_id)
    if not item:
        return None

    item.is_available = is_available
    await session.commit()
    await session.refresh(item)
    return item


async def delete_menu_item(item_id: int, session: AsyncSession):
    """
    Удаляет позицию меню по её ID.
    """
    item = await session.get(MenuItem, item_id)
    if not item:
        raise ValueError("Позиция меню не найдена.")
    await session.delete(item)
    await session.commit()
