from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from back.schemas import (
    OrderCreate,
    OrderOut,
    OrderUpdateStatus,
    Response,
    UserForOrder,
)
from modules.database.connect import get_async_session
from modules.database.methods.orders import (
    create_order_with_items,
    delete_order,
    get_all_orders,
    get_order_by_id as get_order_db,
    get_orders_by_user,
    get_user_id_by_order_id,
    update_order_status,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", status_code=201, response_model=OrderOut)
async def create_new_order(
    order: OrderCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Создаёт новый заказ.
    """
    try:
        return await create_order_with_items(
            user_id=order.user_id,
            delivery_method_id=order.delivery_method_id,
            items=order.items,
            status_id=order.status_id,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Возвращает заказ по его ID.
    """
    try:
        return await get_order_db(order_id=order_id, session=session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=list[OrderOut])
async def list_orders(session: AsyncSession = Depends(get_async_session)):
    """
    Возвращает список всех заказов.
    """
    return await get_all_orders(session=session)


@router.get("/user/{user_id}", response_model=list[OrderOut])
async def get_user_orders(
    user_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает список заказов пользователя.
    """
    return await get_orders_by_user(user_id=user_id, session=session)


@router.get("/{order_id}/user", response_model=UserForOrder)
async def get_user_id_by_order_id_route(
    order_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает ID пользователя по ID заказа.
    """
    try:
        return {
            "user_id": await get_user_id_by_order_id(order_id=order_id, session=session)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{order_id}/status", response_model=Response)
async def update_order_status_route(
    order_id: int,
    status_update: OrderUpdateStatus,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет статус заказа.
    """
    try:
        order = await update_order_status(
            order_id=order_id, status_id=status_update.status_id, session=session
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден.")
    return {"message": "Статус заказа успешно обновлён."}


@router.delete("/{order_id}", status_code=204)
async def delete_order_route(
    order_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет заказ.
    """
    is_deleted = await delete_order(order_id=order_id, session=session)
    if not is_deleted:
        raise HTTPException(status_code=404, detail="Заказ не найден.")
