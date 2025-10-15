from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.database import get_postgres_db
from app.models.user import User
from app.dependencies import get_current_active_user
from uuid import UUID

router = APIRouter(prefix="/categories", tags=["Categories"])

# ======================================================
# GET all categories
# ======================================================
@router.get("", response_model=List[CategoryResponse])
async def get_all_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by name"),
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(Category)

    if search:
        query = query.where((Category.name.ilike(f"%{search}%")))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    categories = result.scalars().all()

    return categories


# ======================================================
# GET category by ID
# ======================================================
@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    print(category)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


# ======================================================
# CREATE category
# ======================================================
@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):

    new_category = Category(
        name=category_data.name,
        description=category_data.description,
        created_by=current_user.id
    )

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return new_category


# ======================================================
# UPDATE category
# ======================================================
@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
        
    # ✅ Authorization check
    if category.created_by != current_user.id: #and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this category"
        )

    # ✅ Update only provided fields
    if category_data.name is not None:
        category.name = category_data.name

    if category_data.description is not None:
        category.description = category_data.description

    await db.commit()
    await db.refresh(category)

    return category


# ======================================================
# DELETE category
# ======================================================
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    await db.delete(category)
    await db.commit()

    return None
