from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from ..models import Order, DeliveryMethod, OrderStatus


async def create_order(
    user_id: int,
    delivery_method_id: int,
    total_price: float,
    status_id: int,
    session: AsyncSession,
) -> Order:
    """
    Создаёт новый заказ.

    :param user_id: Идентификатор пользователя.
    :param delivery_method_id: Идентификатор способа доставки.
    :param total_price: Общая стоимость заказа.
    :param status_id: Идентификатор статуса заказа.
    :param session: Сессия базы данных.
    :return: Объект заказа.
    """
    delivery_method = await session.execute(
        select(DeliveryMethod).where(DeliveryMethod.id == delivery_method_id)
    )
    if not delivery_method.scalars().first():
        raise ValueError("Способ доставки не найден.")

    status = await session.execute(select(OrderStatus).where(OrderStatus.id == status_id))
    if not status.scalars().first():
        raise ValueError("Статус заказа не найден.")

    new_order = Order(
        user_id=user_id,
        delivery_method_id=delivery_method_id,
        total_price=total_price,
        status_id=status_id,
    )
    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)
    return new_order


async def get_order_by_id(order_id: int, session: AsyncSession) -> Order | None:
    """
    Получает заказ по ID.

    :param order_id: ID заказа.
    :param session: Сессия базы данных.
    :return: Объект заказа, если найден, иначе None.
    """
    result = await session.execute(
        select(Order)
        .options(joinedload(Order.delivery_method), joinedload(Order.status))
        .where(Order.id == order_id)
    )
    return result.scalars().first()


async def get_all_orders(session: AsyncSession) -> list[Order]:
    """
    Получает все заказы.

    :param session: Сессия базы данных.
    :return: Список всех заказов.
    """
    result = await session.execute(
        select(Order).options(joinedload(Order.delivery_method), joinedload(Order.status))
    )
    return result.scalars().all()


async def update_order_status(
    order_id: int, status_id: int, session: AsyncSession
) -> Order | None:
    """
    Обновляет статус заказа.

    :param order_id: ID заказа.
    :param status_id: Новый статус заказа.
    :param session: Сессия базы данных.
    :return: Объект обновлённого заказа, если найден, иначе None.
    """
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()

    if not order:
        return None

    status = await session.execute(select(OrderStatus).where(OrderStatus.id == status_id))
    if not status.scalars().first():
        raise ValueError("Статус заказа не найден.")

    order.status_id = status_id
    await session.commit()
    await session.refresh(order)
    return order


async def update_order_price(
    order_id: int, new_price: float, session: AsyncSession
) -> Order | None:
    """
    Обновляет общую стоимость заказа.

    :param order_id: ID заказа.
    :param new_price: Новая стоимость заказа.
    :param session: Сессия базы данных.
    :return: Объект обновлённого заказа, если найден, иначе None.
    """
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()

    if not order:
        return None

    order.total_price = new_price
    await session.commit()
    await session.refresh(order)
    return order


async def delete_order(order_id: int, session: AsyncSession) -> bool:
    """
    Удаляет заказ по ID.

    :param order_id: ID заказа.
    :param session: Сессия базы данных.
    :return: True, если заказ удалён, иначе False.
    """
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()

    if not order:
        return False

    await session.delete(order)
    await session.commit()
    return True


async def get_orders_by_user(user_id: int, session: AsyncSession) -> list[Order]:
    """
    Получает все заказы пользователя.

    :param user_id: Идентификатор пользователя.
    :param session: Сессия базы данных.
    :return: Список заказов пользователя.
    """
    result = await session.execute(
        select(Order)
        .options(joinedload(Order.delivery_method), joinedload(Order.status))
        .where(Order.user_id == user_id)
    )
    return result.scalars().all()
