from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models import DeliveryMethod


async def add_delivery_method(name: str, session: AsyncSession) -> DeliveryMethod:
    """
    Добавляет новый способ доставки.

    :param name: Название способа доставки.
    :param session: Сессия базы данных.
    :return: Объект способа доставки.
    """
    existing_method = await session.execute(
        select(DeliveryMethod).where(DeliveryMethod.name == name)
    )
    if existing_method.scalars().first():
        raise ValueError("Способ доставки с таким названием уже существует.")

    new_method = DeliveryMethod(name=name)
    session.add(new_method)
    await session.commit()
    await session.refresh(new_method)
    return new_method


async def get_delivery_method_by_id(
    delivery_method_id: int, session: AsyncSession
) -> DeliveryMethod | None:
    """
    Получает способ доставки по ID.

    :param delivery_method_id: ID способа доставки.
    :param session: Сессия базы данных.
    :return: Объект способа доставки, если найден, иначе None.
    """
    result = await session.execute(
        select(DeliveryMethod).where(DeliveryMethod.id == delivery_method_id)
    )
    return result.scalars().first()


async def get_all_delivery_methods(session: AsyncSession) -> list[DeliveryMethod]:
    """
    Получает список всех способов доставки.

    :param session: Сессия базы данных.
    :return: Список всех способов доставки.
    """
    result = await session.execute(select(DeliveryMethod))
    return result.scalars().all()


async def delete_delivery_method(
    delivery_method_id: int, session: AsyncSession
) -> bool:
    """
    Удаляет способ доставки по ID.

    :param delivery_method_id: ID способа доставки.
    :param session: Сессия базы данных.
    :return: True, если удалён, иначе False.
    """
    result = await session.execute(
        select(DeliveryMethod).where(DeliveryMethod.id == delivery_method_id)
    )
    delivery_method = result.scalars().first()

    if not delivery_method:
        return False

    await session.delete(delivery_method)
    await session.commit()
    return True
