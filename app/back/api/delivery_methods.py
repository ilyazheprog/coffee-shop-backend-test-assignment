from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from back.schemas import DeliveryMethodCreate, DeliveryMethodOut
from modules.database.connect import get_async_session
from modules.database.methods.delivery_methods import (
    add_delivery_method,
    delete_delivery_method,
    get_all_delivery_methods,
    get_delivery_method_by_id,
)

router = APIRouter(prefix="/delivery-methods", tags=["Delivery Methods"])


@router.post("/", status_code=201, response_model=DeliveryMethodOut)
async def create_delivery_method(
    method: DeliveryMethodCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Создаёт новый способ доставки.
    """
    try:
        return await add_delivery_method(name=method.name, session=session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{delivery_method_id}", response_model=DeliveryMethodOut)
async def get_delivery_method(
    delivery_method_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Получает способ доставки по ID.
    """
    delivery_method = await get_delivery_method_by_id(
        delivery_method_id=delivery_method_id, session=session
    )
    if not delivery_method:
        raise HTTPException(status_code=404, detail="Способ доставки не найден.")
    return delivery_method


@router.get("/", response_model=list[DeliveryMethodOut])
async def list_delivery_methods(session: AsyncSession = Depends(get_async_session)):
    """
    Возвращает список всех способов доставки.
    """
    return await get_all_delivery_methods(session=session)


@router.delete("/{delivery_method_id}", status_code=204)
async def delete_delivery_method_route(
    delivery_method_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет способ доставки по ID.
    """
    deleted = await delete_delivery_method(
        delivery_method_id=delivery_method_id, session=session
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Способ доставки не найден.")
