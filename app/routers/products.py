from app.models.category import Category
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    PaginatedProductResponse,
    PaginationMetadata
)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from typing import Optional
from app.database import get_postgres_db
from app.models.user import User
from app.dependencies import get_current_active_user
from uuid import UUID
import math

router = APIRouter(prefix="/products", tags=["Products"])

# ======================================================
# GET all products
# ======================================================
@router.get("", response_model=PaginatedProductResponse)
async def get_all_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by name"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    stock_status: Optional[str] = Query(None, description="Filter by stock status: red, yellow, green"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    sort_by: Optional[str] = Query(None, description="Sort by field: name, stock, price, created_at, status"),
    order: Optional[str] = Query("asc", description="Sort order: asc or desc"),
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_active_user)
):
    # ============================================================================
    # Build base query for filtering
    # ============================================================================
    base_query = select(Product)

    if search:
        base_query = base_query.where((Product.name.ilike(f"%{search}%")))

    if category_id:
        base_query = base_query.where(Product.category_id == category_id)

    # ============================================================================
    # FILTER by stock_status (red/yellow/green)
    # ============================================================================
    if stock_status:
        status_value = stock_status.lower()
        if status_value == "red":
            # Red: stock == 0
            base_query = base_query.where(Product.stock == 0)
        elif status_value == "yellow":
            # Yellow: 0 < stock <= low_stock_threshold
            base_query = base_query.where(
                (Product.stock > 0) &
                (Product.stock <= Product.low_stock_threshold)
            )
        elif status_value == "green":
            # Green: stock > low_stock_threshold
            base_query = base_query.where(Product.stock > Product.low_stock_threshold)

    # ============================================================================
    # FILTER by price range (min_price and max_price)
    # ============================================================================
    if min_price is not None:
        base_query = base_query.where(Product.price >= min_price)

    if max_price is not None:
        base_query = base_query.where(Product.price <= max_price)

    # ============================================================================
    # Get total count (before pagination)
    # ============================================================================
    # Build count query with same filters as base_query
    count_query = select(func.count(Product.id))

    if search:
        count_query = count_query.where((Product.name.ilike(f"%{search}%")))

    if category_id:
        count_query = count_query.where(Product.category_id == category_id)

    if stock_status:
        status_value = stock_status.lower()
        if status_value == "red":
            count_query = count_query.where(Product.stock == 0)
        elif status_value == "yellow":
            count_query = count_query.where(
                (Product.stock > 0) &
                (Product.stock <= Product.low_stock_threshold)
            )
        elif status_value == "green":
            count_query = count_query.where(Product.stock > Product.low_stock_threshold)

    if min_price is not None:
        count_query = count_query.where(Product.price >= min_price)

    if max_price is not None:
        count_query = count_query.where(Product.price <= max_price)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # ============================================================================
    # Build query with eager loading
    # ============================================================================
    query = base_query.options(
        selectinload(Product.category),
        selectinload(Product.creator),
    )

    # ============================================================================
    # SORTING - Sort by name, stock, price, created_at, or status
    # ============================================================================
    if sort_by:
        if sort_by == "status":
            # ============================================================================
            # Special handling for "status" sorting
            # Status is computed from stock and low_stock_threshold:
            # - red (stock == 0): priority 0 (most urgent)
            # - yellow (0 < stock <= low_stock_threshold): priority 1
            # - green (stock > low_stock_threshold): priority 2 (least urgent)
            # ============================================================================
            status_priority = case(
                (Product.stock == 0, 0),  # red
                (Product.stock <= Product.low_stock_threshold, 1),  # yellow
                else_=2  # green
            )

            # Apply order (asc or desc)
            if order and order.lower() == "desc":
                # desc: green → yellow → red (healthy first)
                query = query.order_by(status_priority.desc())
            else:
                # asc: red → yellow → green (urgent first)
                query = query.order_by(status_priority.asc())
        else:
            # Regular column sorting
            sort_columns = {
                "name": Product.name,
                "stock": Product.stock,
                "price": Product.price,
                "created_at": Product.created_at
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
    products = result.scalars().unique().all()

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

    return PaginatedProductResponse(
        data=products,
        metadata=metadata
    )


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
