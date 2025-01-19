from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from ..models import CartItem, Product


async def add_to_cart(user_id: int, product_id: int, quantity: int, session: AsyncSession) -> CartItem:
    """
    Добавляет продукт в корзину.

    :param user_id: Идентификатор пользователя.
    :param product_id: Идентификатор продукта.
    :param quantity: Количество продукта.
    :param session: Сессия базы данных.
    :return: Объект добавленного элемента корзины.
    """
    # Проверяем, существует ли продукт
    product_result = await session.execute(select(Product).where(Product.id == product_id))
    product = product_result.scalars().first()
    if not product:
        raise ValueError("Продукт не найден.")

    # Проверяем, есть ли уже продукт в корзине
    cart_item_result = await session.execute(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
    )
    cart_item = cart_item_result.scalars().first()

    if cart_item:
        # Обновляем количество и стоимость
        cart_item.quantity += quantity
        cart_item.total_price = cart_item.quantity * product.price
    else:
        # Добавляем новый элемент в корзину
        cart_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_price=quantity * product.price,
        )
        session.add(cart_item)

    await session.commit()
    await session.refresh(cart_item)
    return cart_item


async def get_cart(user_id: int, session: AsyncSession) -> list[CartItem]:
    """
    Получает все элементы корзины пользователя.

    :param user_id: Идентификатор пользователя.
    :param session: Сессия базы данных.
    :return: Список элементов корзины.
    """
    result = await session.execute(
        select(CartItem)
        .options(joinedload(CartItem.product))
        .where(CartItem.user_id == user_id)
    )
    return result.scalars().all()


async def remove_from_cart(user_id: int, product_id: int, session: AsyncSession) -> bool:
    """
    Удаляет продукт из корзины.

    :param user_id: Идентификатор пользователя.
    :param product_id: Идентификатор продукта.
    :param session: Сессия базы данных.
    :return: True, если удалён, иначе False.
    """
    result = await session.execute(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
    )
    cart_item = result.scalars().first()

    if not cart_item:
        return False

    await session.delete(cart_item)
    await session.commit()
    return True


async def clear_cart(user_id: int, session: AsyncSession) -> None:
    """
    Очищает корзину пользователя.

    :param user_id: Идентификатор пользователя.
    :param session: Сессия базы данных.
    """
    await session.execute(
        select(CartItem).where(CartItem.user_id == user_id).delete()
    )
    await session.commit()
