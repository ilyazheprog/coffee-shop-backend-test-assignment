from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models import OrderStatus


async def add_order_status(name: str, session: AsyncSession) -> OrderStatus:
    """
    Добавляет новый статус заказа в базу данных.

    :param name: Имя статуса заказа (уникальное).
    :param session: Сессия базы данных.
    :return: Объект нового статуса заказа.
    """
    existing_status = await session.execute(
        select(OrderStatus).where(OrderStatus.name == name)
    )
    if existing_status.scalars().first():
        raise ValueError("Статус заказа с таким именем уже существует.")
    new_status = OrderStatus(name=name)
    session.add(new_status)
    await session.commit()
    await session.refresh(new_status)
    return new_status


async def get_order_status_by_id(
    status_id: int, session: AsyncSession
) -> OrderStatus | None:
    """
    Возвращает объект статуса заказа по его ID.

    :param status_id: ID статуса заказа.
    :param session: Сессия базы данных.
    :return: Объект статуса заказа, если найден, иначе None.
    """
    result = await session.execute(
        select(OrderStatus).where(OrderStatus.id == status_id)
    )
    return result.scalars().first()


async def get_all_order_statuses(session: AsyncSession) -> list[OrderStatus]:
    """
    Возвращает список всех статусов заказов.

    :param session: Сессия базы данных.
    :return: Список всех статусов заказов.
    """
    result = await session.execute(select(OrderStatus))
    return result.scalars().all()


async def update_order_status_name(
    status_id: int, new_name: str, session: AsyncSession
) -> OrderStatus | None:
    """
    Обновляет имя статуса заказа.

    :param status_id: ID статуса заказа.
    :param new_name: Новое имя статуса заказа.
    :param session: Сессия базы данных.
    :return: Объект статуса заказа с обновленным именем, если найден, иначе None.
    """
    result = await session.execute(
        select(OrderStatus).where(OrderStatus.id == status_id)
    )
    status = result.scalars().first()
    if status:
        existing_status = await session.execute(
            select(OrderStatus).where(OrderStatus.name == new_name)
        )
        if existing_status.scalars().first():
            raise ValueError("Статус заказа с таким именем уже существует.")
        status.name = new_name
        await session.commit()
        await session.refresh(status)
    return status


async def delete_order_status(status_id: int, session: AsyncSession) -> bool:
    """
    Удаляет статус заказа по его ID.

    :param status_id: ID статуса заказа.
    :param session: Сессия базы данных.
    :return: True, если статус заказа удален, иначе False.
    """
    status = await session.get(OrderStatus, status_id)
    if not status:
        return False
    await session.delete(status)
    await session.commit()
    return True
