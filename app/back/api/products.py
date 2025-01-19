from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from back.schemas import ProductCreate, ProductOut, ProductUpdate
from modules.database.connect import get_async_session
from modules.database.methods.products import (
    add_product,
    get_product_by_id,
    get_all_products,
    update_product,
    delete_product,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductOut)
async def create_product(
    product: ProductCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Создаёт новый продукт.
    """
    try:
        new_product = await add_product(
            name=product.name,
            price=product.price,
            in_stock=product.in_stock,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_product


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Получает продукт по ID.
    """
    product = await get_product_by_id(product_id=product_id, session=session)
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден.")
    return product


@router.get("/", response_model=list[ProductOut])
async def list_products(session: AsyncSession = Depends(get_async_session)):
    """
    Возвращает весь ассортимент продуктов.
    """
    return await get_all_products(session=session)


@router.put("/{product_id}", response_model=ProductOut)
async def update_product_route(
    product_id: int,
    product_update: ProductUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет данные продукта.
    """
    updated_product = await update_product(
        product_id=product_id,
        name=product_update.name,
        price=product_update.price,
        in_stock=product_update.in_stock,
        session=session,
    )
    if not updated_product:
        raise HTTPException(status_code=404, detail="Продукт не найден.")
    return updated_product


@router.delete("/{product_id}")
async def delete_product_route(
    product_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет продукт по ID.
    """
    deleted = await delete_product(product_id=product_id, session=session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Продукт не найден.")
    return {"message": "Продукт успешно удалён."}
