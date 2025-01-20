from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import MenuCategory

async def get_all_categories(session: AsyncSession) -> list[MenuCategory]:
    result = await session.execute(select(MenuCategory))
    return result.scalars().all()

async def create_category(name: str, session: AsyncSession) -> MenuCategory:
    existing = await session.execute(select(MenuCategory).where(MenuCategory.name == name))
    if existing.scalars().first():
        raise ValueError("Категория с таким названием уже существует.")
    category = MenuCategory(name=name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category

async def delete_category(category_id: int, session: AsyncSession):
    category = await session.get(MenuCategory, category_id)
    if not category:
        raise ValueError("Категория не найдена.")
    await session.delete(category)
    await session.commit()