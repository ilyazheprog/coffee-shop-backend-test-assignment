from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import insert
from ..models import Order, DeliveryMethod, OrderStatus, MenuItem, order_menu_items


async def create_order_with_items(
    user_id: int,
    delivery_method_id: int,
    items: list[dict],  # [{"menu_item_id": 1, "quantity": 2}, ...]
    status_id: int,
    session: AsyncSession,
) -> Order:
    """
    Создаёт новый заказ с позициями меню.

    :param user_id: Идентификатор пользователя.
    :param delivery_method_id: Идентификатор способа доставки.
    :param items: Список позиций меню и их количества.
    :param status_id: Идентификатор статуса заказа.
    :param session: Сессия базы данных.
    :return: Объект заказа.
    """
    delivery_method = await session.get(DeliveryMethod, delivery_method_id)
    if not delivery_method:
        raise ValueError("Способ доставки не найден.")

    status = await session.get(OrderStatus, status_id)
    if not status:
        raise ValueError("Статус заказа не найден.")

    total_price = 0
    order_items = []
    for item in items:
        menu_item = await session.get(MenuItem, item["menu_item_id"])
        if not menu_item:
            raise ValueError(f"Позиция меню с ID {item['menu_item_id']} не найдена.")
        total_price += menu_item.price * item["quantity"]
        order_items.append({"menu_item_id": menu_item.id, "quantity": item["quantity"]})

    new_order = Order(
        user_id=user_id,
        delivery_method_id=delivery_method_id,
        total_price=total_price,
        status_id=status_id,
    )
    session.add(new_order)
    await session.commit()

    for order_item in order_items:
        await session.execute(
            insert(order_menu_items).values(
                order_id=new_order.id,
                menu_item_id=order_item["menu_item_id"],
                quantity=order_item["quantity"],
            )
        )

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


async def update_order_status(order_id: int, status_id: int, session: AsyncSession) -> Order | None:
    """
    Обновляет статус заказа.

    :param order_id: ID заказа.
    :param status_id: Новый статус заказа.
    :param session: Сессия базы данных.
    :return: Объект обновлённого заказа, если найден.
    """
    order = await session.get(Order, order_id)
    if not order:
        return None

    status = await session.get(OrderStatus, status_id)
    if not status:
        raise ValueError("Статус заказа не найден.")

    order.status_id = status_id
    await session.commit()
    await session.refresh(order)
    return order


async def update_order_price(order_id: int, new_price: float, session: AsyncSession) -> Order | None:
    """
    Обновляет общую стоимость заказа.

    :param order_id: ID заказа.
    :param new_price: Новая стоимость заказа.
    :param session: Сессия базы данных.
    :return: Объект обновлённого заказа, если найден.
    """
    order = await session.get(Order, order_id)
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
    order = await session.get(Order, order_id)
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


async def get_order_with_items(order_id: int, session: AsyncSession) -> dict:
    """
    Получает заказ с его позициями.

    :param order_id: ID заказа.
    :param session: Сессия базы данных.
    :return: Словарь с информацией о заказе.
    """
    result = await session.execute(
        select(Order)
        .options(
            joinedload(Order.delivery_method),
            joinedload(Order.status),
            joinedload(Order.menu_items),
        )
        .where(Order.id == order_id)
    )
    order = result.scalars().first()

    if not order:
        raise ValueError("Заказ не найден.")

    return {
        "id": order.id,
        "user_id": order.user_id,
        "delivery_method": order.delivery_method.name,
        "status": order.status.name,
        "total_price": order.total_price,
        "menu_items": [
            {
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "quantity": item.quantity,
            }
            for item in order.menu_items
        ],
    }



async def get_all_orders_with_items(session: AsyncSession) -> list[dict]:
    """
    Получает все заказы с их позициями.

    :param session: Сессия базы данных.
    :return: Список заказов.
    """
    result = await session.execute(
        select(Order)
        .options(
            joinedload(Order.delivery_method),
            joinedload(Order.status),
            joinedload(Order.menu_items),
        )
    )
    orders = result.scalars().all()

    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "delivery_method": order.delivery_method.name,
            "status": order.status.name,
            "total_price": order.total_price,
            "menu_items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "price": item.price,
                    "quantity": item.quantity,
                }
                for item in order.menu_items
            ],
        }
        for order in orders
    ]
