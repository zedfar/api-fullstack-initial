from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.database import get_postgres_db
from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleResponse, RoleCreate, RoleUpdate
from app.dependencies import get_current_active_user
# from app.utils.security import get_password_hash

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("", response_model=List[RoleResponse])
async def get_all_roles(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: str = Query(None, description="Search by username or email"),
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(Role)

    if search:
        query = query.where(
            (Role.name.ilike(f"%{search}%"))
        )

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    roles = result.scalars().all()

    return roles

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    
    print(role)

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    return role

@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Role).where(
            (Role.name == role_data.name)
        )
    )
    existing_role = result.scalar_one_or_none()

    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already registered"
        )
# 
    # hashed_password = get_password_hash(_data.password)

    new_role = Role(
        name=role_data.name,
        description=role_data.description
    )

    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)

    return new_role

@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )


    # ✅ Update name dengan validasi duplikat
    if role_data.name is not None:
        existing = await db.execute(
            select(Role).where(Role.name == role_data.name, Role.id != role_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already taken"
            )
        role.name = role_data.name
        
    # ✅ Update description tanpa tergantung name
    if role_data.description is not None:
        role.description = role_data.description

    await db.commit()
    await db.refresh(role)

    return role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    await db.delete(role)
    await db.commit()

    return None
