from app.schemas.category import CategorySimple
from app.schemas.user import UserSimple
from pydantic import BaseModel, Field
from typing import Optional
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

    class Config:
        from_attributes = True
