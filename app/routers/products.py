from app.models.category import Category
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database import get_postgres_db
from app.models.user import User
from app.dependencies import get_current_active_user
from uuid import UUID

router = APIRouter(prefix="/products", tags=["Products"])

# ======================================================
# GET all products
# ======================================================
@router.get("", response_model=List[ProductResponse])
async def get_all_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by name"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    query = (
        select(Product)
        .options(
            selectinload(Product.category),
            selectinload(Product.creator),
        )
    )

    if search:
        query = query.where((Product.name.ilike(f"%{search}%")))
        
    if category_id:
        query = query.where(Product.category_id == category_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    products = result.scalars().unique().all()

    return products


# ======================================================
# GET product by ID
# ======================================================
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.category),
            selectinload(Product.creator),
        )
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    # print(product)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


# ======================================================
# CREATE product
# ======================================================
@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    
    category = await db.get(Category, product_data.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        low_stock_threshold=product_data.low_stock_threshold,
        image_url=product_data.image_url,
        category_id=product_data.category_id,
        created_by=current_user.id,
    )

    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    return new_product


# ======================================================
# UPDATE product
# ======================================================
@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
        
    # ✅ Authorization optional: only owner or admin can update
    # if product.created_by != current_user.id and not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Not authorized to update this product")

    # ✅ Update only provided fields
    update_fields = product_data.dict(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)

    return product


# ======================================================
# DELETE product
# ======================================================
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    product_id: UUID,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
        
    # ✅ Optional: only owner or admin can delete
    # if product.created_by != current_user.id and not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    await db.delete(product)
    await db.commit()

    return None
