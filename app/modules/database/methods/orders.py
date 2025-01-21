from typing import Literal

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from back.schemas.orders import MenuItemInOrder

from ..models import DeliveryMethod, MenuItem, Order, OrderMenuItem, OrderStatus


async def create_order_with_items(
    user_id: int,
    delivery_method_id: int,
    items: list[MenuItemInOrder],
    status_id: int,
    session: AsyncSession,
) -> dict[
    Literal[
        "id",
        "user_id",
        "delivery_method_id",
        "delivery_method_name",
        "status_id",
        "status_name",
        "total_price",
        "created_at",
        "items",
    ]
]:
    """
    Создаёт новый заказ с позициями меню.

    :param user_id: ID пользователя.
    :param delivery_method_id: ID способа доставки.
    :param items: Список позиций меню.
    :param status_id: ID статуса заказа.
    :param session: Сессия базы данных.
    :return: Информация о созданном заказе.
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
        menu_item = await session.get(MenuItem, item.menu_item_id)
        if not menu_item:
            raise ValueError(f"Позиция меню с ID {item.menu_item_id} не найдена.")
        total_price += menu_item.price * item.quantity
        order_items.append({"menu_item_id": menu_item.id, "quantity": item.quantity})

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
            insert(OrderMenuItem).values(
                order_id=new_order.id,
                menu_item_id=order_item["menu_item_id"],
                quantity=order_item["quantity"],
            )
        )

    await session.commit()
    await session.refresh(new_order)

    return {
        "id": new_order.id,
        "user_id": new_order.user_id,
        "delivery_method_id": new_order.delivery_method_id,
        "delivery_method_name": new_order.delivery_method.name,
        "status_id": new_order.status_id,
        "status_name": new_order.status.name,
        "total_price": new_order.total_price,
        "created_at": new_order.created_at,
        "items": order_items,
    }


async def get_order_by_id(order_id: int, session: AsyncSession) -> (
    dict[
        Literal[
            "id",
            "user_id",
            "delivery_method_id",
            "delivery_method_name",
            "status_id",
            "status_name",
            "total_price",
            "created_at",
        ]
        | Literal["items"],
        list[dict[Literal["menu_item_id", "name", "price", "quantity"]]],
    ]
    | None
):
    """
    Получает заказ по его ID.

    :param order_id: ID заказа.
    :param session: Сессия базы данных.
    :return: Информация о заказе, если найден, иначе None.
    """
    result = await session.execute(
        select(Order)
        .options(
            selectinload(Order.delivery_method),
            selectinload(Order.status),
            selectinload(Order.menu_items).selectinload(MenuItem.order_menu_items),
        )
        .where(Order.id == order_id)
    )
    order = result.scalars().first()

    if not order:
        return None

    return {
        "id": order.id,
        "user_id": order.user_id,
        "delivery_method_id": order.delivery_method_id,
        "delivery_method_name": order.delivery_method.name,
        "status_id": order.status_id,
        "status_name": order.status.name,
        "total_price": order.total_price,
        "created_at": order.created_at,
        "items": [
            {
                "menu_item_id": item.id,
                "name": item.name,
                "price": item.price,
                "quantity": next(
                    (
                        omi.quantity
                        for omi in item.order_menu_items
                        if omi.order_id == order.id
                    ),
                    1,
                ),
            }
            for item in order.menu_items
        ],
    }


async def get_all_orders(session: AsyncSession) -> list[dict]:
    """
    Получает все заказы.

    :param session: Сессия базы данных.
    :return: Список всех заказов.
    """
    result = await session.execute(
        select(Order).options(
            selectinload(Order.delivery_method),
            selectinload(Order.status),
            selectinload(Order.menu_items).selectinload(MenuItem.order_menu_items),
        )
    )
    orders = result.scalars().all()

    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "delivery_method_id": order.delivery_method_id,
            "delivery_method_name": order.delivery_method.name,
            "status_id": order.status_id,
            "status_name": order.status.name,
            "total_price": order.total_price,
            "created_at": order.created_at,
            "items": [
                {
                    "menu_item_id": item.id,
                    "name": item.name,
                    "price": item.price,
                    "quantity": next(
                        (
                            omi.quantity
                            for omi in item.order_menu_items
                            if omi.order_id == order.id
                        ),
                        1,
                    ),
                }
                for item in order.menu_items
            ],
        }
        for order in orders
    ]


async def get_orders_by_user(user_id: int, session: AsyncSession) -> list[dict]:
    """
    Получает все заказы пользователя.

    :param user_id: ID пользователя.
    :param session: Сессия базы данных.
    :return: Список всех заказов пользователя.
    """
    result = await session.execute(
        select(Order)
        .options(
            selectinload(Order.delivery_method),
            selectinload(Order.status),
            selectinload(Order.menu_items).selectinload(MenuItem.order_menu_items),
        )
        .where(Order.user_id == user_id)
    )
    orders = result.scalars().all()

    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "delivery_method_id": order.delivery_method_id,
            "delivery_method_name": order.delivery_method.name,
            "status_id": order.status_id,
            "status_name": order.status.name,
            "total_price": order.total_price,
            "created_at": order.created_at,
            "items": [
                {
                    "menu_item_id": item.id,
                    "name": item.name,
                    "price": item.price,
                    "quantity": next(
                        (
                            omi.quantity
                            for omi in item.order_menu_items
                            if omi.order_id == order.id
                        ),
                        1,
                    ),
                }
                for item in order.menu_items
            ],
        }
        for order in orders
    ]


async def get_user_id_by_order_id(order_id: int, session: AsyncSession) -> int:
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    return order.user_id


async def update_order_status(
    order_id: int, status_id: int, session: AsyncSession
) -> bool:
    order = await session.get(Order, order_id)
    if not order:
        return False

    status = await session.get(OrderStatus, status_id)
    if not status:
        return False
    order.status_id = status_id
    await session.commit()
    await session.refresh(order)
    return True


async def delete_order(order_id: int, session: AsyncSession) -> bool:
    order = await session.get(Order, order_id)
    if not order:
        return False

    await session.delete(order)
    await session.commit()
    return True
