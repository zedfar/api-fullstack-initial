from app.schemas.user import UserSimple
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    created_by: Optional[uuid.UUID] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: uuid.UUID
    creator: Optional[UserSimple] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategorySimple(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True