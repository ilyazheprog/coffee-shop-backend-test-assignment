from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Product

async def add_product(name: str, price: float, in_stock: bool, session: AsyncSession) -> Product:
    """
    Добавляет новый продукт в базу данных.

    :param name: Название продукта.
    :param price: Цена продукта.
    :param in_stock: Наличие продукта.
    :param session: Сессия базы данных.
    :return: Объект нового продукта.
    """
    existing_product = await session.execute(select(Product).where(Product.name == name))
    if existing_product.scalars().first():
        raise ValueError("Продукт с таким названием уже существует.")

    new_product = Product(name=name, price=price, in_stock=in_stock)
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product


async def get_product_by_id(product_id: int, session: AsyncSession) -> Product | None:
    """
    Получает продукт по ID.

    :param product_id: ID продукта.
    :param session: Сессия базы данных.
    :return: Объект продукта, если найден, иначе None.
    """
    result = await session.execute(select(Product).where(Product.id == product_id))
    return result.scalars().first()


async def get_all_products(session: AsyncSession) -> list[Product]:
    """
    Получает весь ассортимент продуктов.

    :param session: Сессия базы данных.
    :return: Список продуктов.
    """
    result = await session.execute(select(Product))
    return result.scalars().all()


async def update_product(product_id: int, name: str, price: float, in_stock: bool, session: AsyncSession) -> Product | None:
    """
    Обновляет данные продукта.

    :param product_id: ID продукта.
    :param name: Новое название продукта.
    :param price: Новая цена продукта.
    :param in_stock: Обновленное состояние наличия.
    :param session: Сессия базы данных.
    :return: Обновлённый продукт, если найден, иначе None.
    """
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()

    if not product:
        return None

    product.name = name
    product.price = price
    product.in_stock = in_stock
    await session.commit()
    await session.refresh(product)
    return product


async def delete_product(product_id: int, session: AsyncSession) -> bool:
    """
    Удаляет продукт по ID.

    :param product_id: ID продукта.
    :param session: Сессия базы данных.
    :return: True, если удалён, иначе False.
    """
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()

    if not product:
        return False

    await session.delete(product)
    await session.commit()
    return True
