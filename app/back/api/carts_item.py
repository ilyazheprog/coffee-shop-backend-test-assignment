from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from back.schemas import CartItemCreate, CartItemOut, CartOut
from modules.database.connect import get_async_session
from modules.database.methods.carts_item import add_to_cart, get_cart, remove_from_cart, clear_cart

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/", response_model=CartItemOut)
async def add_item_to_cart(
    user_id: int,
    item: CartItemCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Добавляет продукт в корзину.
    """
    try:
        cart_item = await add_to_cart(
            user_id=user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return cart_item


@router.get("/", response_model=CartOut)
async def get_user_cart(user_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Получает корзину пользователя.
    """
    cart_items = await get_cart(user_id=user_id, session=session)
    return {"items": cart_items}


@router.delete("/{product_id}")
async def remove_item_from_cart(
    user_id: int, product_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет продукт из корзины.
    """
    deleted = await remove_from_cart(user_id=user_id, product_id=product_id, session=session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Продукт не найден в корзине.")
    return {"message": "Продукт успешно удалён из корзины."}


@router.delete("/")
async def clear_user_cart(user_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Очищает корзину пользователя.
    """
    await clear_cart(user_id=user_id, session=session)
    return {"message": "Корзина успешно очищена."}
