from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from back.schemas import OrderStatusCreate, OrderStatusOut, OrderStatusUpdate
from modules.database.connect import get_async_session
from modules.database.methods.order_statuses import (
    add_order_status,
    delete_order_status,
    get_all_order_statuses,
    get_order_status_by_id,
    update_order_status_name,
)

router = APIRouter(prefix="/order-statuses", tags=["Order Statuses"])


@router.post("/", status_code=201, response_model=OrderStatusOut)
async def add_order_status(
    order_status: OrderStatusCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Добавляет новый статус заказа в базу данных.
    """
    try:
        return await add_order_status(name=order_status.name, session=session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{status_id}", response_model=OrderStatusOut)
async def get_order_status(
    status_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает объект статуса заказа по его ID.
    """
    status = await get_order_status_by_id(status_id=status_id, session=session)
    if not status:
        raise HTTPException(status_code=404, detail="Статус заказа не найден.")
    return status


@router.get("/", response_model=list[OrderStatusOut])
async def list_order_statuses(session: AsyncSession = Depends(get_async_session)):
    """
    Возвращает список всех статусов заказов.
    """
    return await get_all_order_statuses(session=session)


@router.put("/{status_id}", response_model=OrderStatusOut)
async def update_order_status_name(
    status_id: int,
    order_status: OrderStatusUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет имя статуса заказа.
    """
    try:
        return await update_order_status_name(
            status_id=status_id, new_name=order_status.name, session=session
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{status_id}", status_code=204)
async def delete_order_status(
    status_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет статус заказа из базы данных.
    """
    status = await get_order_status_by_id(status_id=status_id, session=session)
    if not status:
        raise HTTPException(status_code=404, detail="Статус заказа не найден.")
    await delete_order_status(status_id=status_id, session=session)
