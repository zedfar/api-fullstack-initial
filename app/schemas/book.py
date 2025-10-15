from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    isbn: Optional[str] = Field(None, max_length=20)
    published_year: Optional[int] = Field(None, ge=1000, le=9999)
    price: Optional[float] = Field(None, ge=0)

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    isbn: Optional[str] = Field(None, max_length=20)
    published_year: Optional[int] = Field(None, ge=1000, le=9999)
    price: Optional[float] = Field(None, ge=0)

class BookResponse(BookBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
