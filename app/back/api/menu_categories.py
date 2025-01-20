from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from modules.database.connect import get_async_session
from modules.database.methods.menu_categories import *
from back.schemas import MenuCategoryCreate, MenuCategoryOut

router = APIRouter(prefix="/menu-categories", tags=["Menu Categories"])

@router.get("/", response_model=list[MenuCategoryOut])
async def list_categories(session: AsyncSession = Depends(get_async_session)):
    return await get_all_categories(session)

@router.post("/", response_model=MenuCategoryOut, status_code=201)
async def create_category_endpoint(category: MenuCategoryCreate, session: AsyncSession = Depends(get_async_session)):
    try:
        return await create_category(category.name, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{category_id}")
async def delete_category_endpoint(category_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        await delete_category(category_id, session)
        return {"message": "Категория успешно удалена."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
