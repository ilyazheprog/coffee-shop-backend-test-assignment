from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from back.schemas import UserCreate, UserOut, RoleChange
from modules.database.connect import get_async_session
from modules.database.methods.users import (
    add_user,
    get_user_by_tg_id,
    get_all_users,
    change_user_role,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserOut)
async def create_user(
    user: UserCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Создаёт нового пользователя.
    """
    try:
        new_user = await add_user(
            tg_id=user.tg_id,
            role_id=user.role_id,
            username=user.username,
            session=session,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_user


@router.get("/{tg_id}", response_model=UserOut)
async def get_user(tg_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Получает пользователя по Telegram ID.
    """
    user = await get_user_by_tg_id(tg_id=tg_id, session=session)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    return user


@router.get("/", response_model=list[UserOut])
async def list_users(session: AsyncSession = Depends(get_async_session)):
    """
    Возвращает список всех пользователей.
    """
    return await get_all_users(session=session)


@router.put("/change-role/{tg_id}", response_model=UserOut)
async def change_role(
    tg_id: int,
    role_change: RoleChange,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Изменяет роль пользователя.
    """
    user = await change_user_role(
        tg_id=tg_id, new_role_id=role_change.new_role_id, session=session
    )
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    return user
