from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from back.schemas import RoleCreate, RoleOut, RoleUpdate, UserIDs
from modules.database.connect import get_async_session
from modules.database.methods.roles import (
    add_role,
    delete_role,
    get_all_roles,
    get_role_by_id,
    get_users_by_role_id,
    update_role_name,
)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=RoleOut)
async def create_role(
    role: RoleCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Создаёт новую роль.
    """
    try:
        new_role = await add_role(name=role.name, session=session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return new_role


@router.get("/{role_id}", response_model=RoleOut)
async def get_role(role_id: int, session: AsyncSession = Depends(get_async_session)):
    """
    Получает роль по ID.
    """
    role = await get_role_by_id(role_id=role_id, session=session)

    if not role:
        raise HTTPException(status_code=404, detail="Роль не найдена.")
    return role


@router.put("/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет имя роли.
    """
    updated_role = await update_role_name(
        role_id=role_id, new_name=role_update.name, session=session
    )
    if not updated_role:
        raise HTTPException(status_code=404, detail="Роль не найдена.")
    return updated_role


@router.get("/", response_model=list[RoleOut])
async def list_roles(session: AsyncSession = Depends(get_async_session)):
    """
    Возвращает список всех ролей.
    """
    return await get_all_roles(session=session)


@router.get("/users/{role_id}", response_model=UserIDs)
async def get_users_by_role(
    role_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает список пользователей с данной ролью.
    """
    return {"user_ids": await get_users_by_role_id(role_id=role_id, session=session)}


@router.delete("/{role_id}", status_code=204)
async def delete_role_by_id(
    role_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет роль по ID.
    """
    deleted = await delete_role(role_id=role_id, session=session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Роль не найдена.")
