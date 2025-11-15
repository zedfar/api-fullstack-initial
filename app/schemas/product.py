from app.schemas.category import CategorySimple
from app.schemas.user import UserSimple
from pydantic import BaseModel, Field, computed_field
from typing import Optional, Literal, List
from datetime import datetime
import uuid


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=255)
    category_id: uuid.UUID


class ProductCreate(ProductBase):
    created_by: Optional[uuid.UUID] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=255)
    category_id: Optional[uuid.UUID] = None


class ProductResponse(ProductBase):
    id: uuid.UUID
    creator: Optional[UserSimple] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategorySimple] = None

    @computed_field
    @property
    def stock_status(self) -> Literal["red", "yellow", "green"]:
        """
        Compute stock status based on stock level:
        - red: stock == 0 (out of stock)
        - yellow: 0 < stock <= low_stock_threshold (low stock warning)
        - green: stock > low_stock_threshold (healthy stock)
        """
        if self.stock == 0:
            return "red"
        elif self.stock <= (self.low_stock_threshold or 10):
            return "yellow"
        else:
            return "green"

    class Config:
        from_attributes = True


# ============================================================================
# Pagination Schemas
# ============================================================================
class PaginationMetadata(BaseModel):
    """Metadata for pagination"""
    total: int = Field(..., description="Total number of records")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Number of records per page")
    page: int = Field(..., description="Current page number (1-indexed)")
    total_pages: int = Field(..., description="Total number of pages")


class PaginatedProductResponse(BaseModel):
    """Response with pagination metadata"""
    data: List[ProductResponse]
    metadata: PaginationMetadata
