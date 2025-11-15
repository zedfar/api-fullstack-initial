# from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from app.schemas.role import RoleSimple
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role_id: Optional[uuid.UUID] = None
    # category_id: uuid.UUID = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    is_active: Optional[bool] = None
    role_id: Optional[uuid.UUID] = None
    # category_id: uuid.UUID = None


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: Optional[RoleSimple] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class UserSimple(BaseModel):
    id: uuid.UUID
    username: str

    class Config:
        from_attributes = True
        
class UserLoginMetadata(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    role: Optional[RoleSimple] = None

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


class PaginatedUserResponse(BaseModel):
    """Response with pagination metadata"""
    data: List[UserResponse]
    metadata: PaginationMetadata