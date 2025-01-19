from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from back.schemas.orders import (
    OrderCreate,
    OrderOut,
    OrderUpdateStatus,
    OrderUpdatePrice,
)
from modules.database.connect import get_async_session
from modules.database.methods.orders import (
    create_order,
    get_order_by_id,
    get_all_orders,
    update_order_status,
    update_order_price,
    delete_order,
    get_orders_by_user,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderOut)
async def create_new_order(
    order: OrderCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Создаёт новый заказ.
    """
    try:
        return await create_order(
            user_id=order.user_id,
            delivery_method_id=order.delivery_method_id,
            total_price=order.total_price,
            status_id=order.status_id,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Получает заказ по ID.
    """
    order = await get_order_by_id(order_id=order_id, session=session)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден.")
    return order


@router.get("/", response_model=list[OrderOut])
async def list_orders(session: AsyncSession = Depends(get_async_session)):
    """
    Получает список всех заказов.
    """
    return await get_all_orders(session=session)


@router.get("/user/{user_id}", response_model=list[OrderOut])
async def get_user_orders(
    user_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Получает все заказы пользователя.
    """
    return await get_orders_by_user(user_id=user_id, session=session)


@router.put("/{order_id}/status", response_model=OrderOut)
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
    return order


@router.put("/{order_id}/price", response_model=OrderOut)
async def update_order_price_route(
    order_id: int,
    price_update: OrderUpdatePrice,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет стоимость заказа.
    """
    order = await update_order_price(
        order_id=order_id, new_price=price_update.total_price, session=session
    )
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден.")
    return order


@router.delete("/{order_id}")
async def delete_order_route(
    order_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет заказ по ID.
    """
    is_deleted = await delete_order(order_id=order_id, session=session)
    if not is_deleted:
        raise HTTPException(status_code=404, detail="Заказ не найден.")
    return {"message": "Заказ успешно удалён."}
