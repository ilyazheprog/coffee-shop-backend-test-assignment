from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from back.schemas import MenuCategoryCreate, MenuCategoryOut
from modules.database.connect import get_async_session
from modules.database.methods.menu_categories import (
    create_category,
    delete_category,
    get_all_categories,
)

router = APIRouter(prefix="/menu-categories", tags=["Menu Categories"])


@router.get("/", response_model=list[MenuCategoryOut])
async def list_categories(session: AsyncSession = Depends(get_async_session)):
    """
    Возвращает список всех категорий меню.
    """
    return await get_all_categories(session)


@router.post("/", status_code=201, response_model=MenuCategoryOut)
async def create_category_endpoint(
    category: MenuCategoryCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Создаёт новую категорию меню.
    """
    try:
        return await create_category(category.name, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}", status_code=204)
async def delete_category_endpoint(
    category_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет категорию меню по её ID.
    """
    try:
        await delete_category(category_id, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
