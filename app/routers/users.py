from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from typing import Optional
from app.database import get_postgres_db
from app.models.user import User
from app.models.role import Role
from app.schemas.user import (
    UserResponse,
    UserCreate,
    UserUpdate,
    PaginatedUserResponse,
    PaginationMetadata
)
from app.dependencies import get_current_active_user
from app.utils.security import get_password_hash
import math

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedUserResponse)
async def get_all_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: str = Query(None, description="Search by username or email"),
    sort_by: Optional[str] = Query(None, description="Sort by field: username, email, full_name, created_at"),
    order: Optional[str] = Query("asc", description="Sort order: asc or desc"),
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    # ============================================================================
    # Build base query for filtering
    # ============================================================================
    base_query = select(User)

    if search:
        base_query = base_query.where(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )

    # ============================================================================
    # Get total count (before pagination)
    # ============================================================================
    count_query = select(func.count()).select_from(base_query.alias())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # ============================================================================
    # Build query with eager loading
    # ============================================================================
    query = base_query.options(selectinload(User.role))

    # ============================================================================
    # SORTING - Sort by username, email, full_name, or created_at
    # ============================================================================
    if sort_by:
        sort_columns = {
            "username": User.username,
            "email": User.email,
            "full_name": User.full_name,
            "created_at": User.created_at
        }

        if sort_by in sort_columns:
            column = sort_columns[sort_by]
            # Apply order (asc or desc)
            if order and order.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

    # ============================================================================
    # Apply pagination
    # ============================================================================
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    # ============================================================================
    # Calculate pagination metadata
    # ============================================================================
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = math.ceil(total / limit) if limit > 0 else 0

    metadata = PaginationMetadata(
        total=total,
        skip=skip,
        limit=limit,
        page=page,
        total_pages=total_pages
    )

    return PaginatedUserResponse(
        data=users,
        metadata=metadata
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (
                User.username == user_data.username)
        )
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )

    hashed_password = get_password_hash(user_data.password)

    # role_result = await db.execute(select(Role).where(Role.name == "admin"))
    # admin_role = role_result.scalar_one_or_none()

    # if not admin_role:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Default role 'admin' not found"
    #     )

    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role_id=user_data.role_id
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # ============================================================================
    # Reload user with role relationship for response
    # ============================================================================
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == new_user.id)
    )
    user_with_role = result.scalar_one()

    return user_with_role


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    # ============================================================================
    # Load user with role relationship
    # ============================================================================
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user_data.email is not None:
        existing = await db.execute(
            select(User).where(User.email ==
                               user_data.email, User.id != user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email

    if user_data.username is not None:
        existing = await db.execute(
            select(User).where(User.username ==
                               user_data.username, User.id != user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = user_data.username

    if user_data.full_name is not None:
        user.full_name = user_data.full_name

    if user_data.password is not None:
        user.hashed_password = get_password_hash(user_data.password)

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.role_id is not None:
        user.role_id = user_data.role_id

    await db.commit()
    await db.refresh(user)

    # ============================================================================
    # Reload user with role relationship if role_id was updated
    # This ensures the response includes the updated role object
    # ============================================================================
    if user_data.role_id is not None:
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user_id)
        )
        user = result.scalar_one()

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await db.delete(user)
    await db.commit()

    return None
