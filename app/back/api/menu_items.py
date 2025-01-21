from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from back.schemas import MenuItemCreate, MenuItemOut
from modules.database.connect import get_async_session
from modules.database.methods.menu_items import (
    create_menu_item,
    delete_menu_item,
    get_all_menu_items,
    get_menu_item_by_id,
    update_menu_item,
    update_menu_item_availability,
)

router = APIRouter(prefix="/menu-items", tags=["Menu Items"])


@router.get("/", response_model=list[MenuItemOut])
async def list_menu_items(
    category_id: int = None,
    is_available: bool = None,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает список всех позиций меню.
    """
    return await get_all_menu_items(category_id, is_available, session)


@router.get("/{item_id}", response_model=MenuItemOut)
async def get_menu_item(
    item_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает позицию меню по её ID.
    """
    item = await get_menu_item_by_id(item_id, session)
    if not item:
        raise HTTPException(status_code=404, detail="Позиция меню не найдена.")
    return item


@router.post("/", response_model=MenuItemOut, status_code=201)
async def create_menu_item_endpoint(
    item: MenuItemCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Создаёт новую позицию в меню.
    """
    return await create_menu_item(
        item.name, item.category_id, item.weight, item.price, item.is_available, session
    )


@router.put("/{item_id}", response_model=MenuItemOut)
async def update_menu_item_endpoint(
    item_id: int,
    item_data: MenuItemCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет данные позиции меню.
    """
    updated_item = await update_menu_item(
        item_id,
        name=item_data.name,
        category_id=item_data.category_id,
        weight=item_data.weight,
        price=item_data.price,
        is_available=item_data.is_available,
        session=session,
    )
    if not updated_item:
        raise HTTPException(status_code=404, detail="Позиция меню не найдена.")
    return updated_item


@router.put("/{item_id}/availability", response_model=MenuItemOut)
async def update_menu_item_availability_endpoint(
    item_id: int,
    is_available: bool,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет доступность позиции меню.
    """
    updated_item = await update_menu_item_availability(item_id, is_available, session)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Позиция меню не найдена.")
    return updated_item


@router.delete("/{item_id}", status_code=204)
async def delete_menu_item_endpoint(
    item_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет позицию меню по её ID.
    """
    try:
        await delete_menu_item(item_id, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
