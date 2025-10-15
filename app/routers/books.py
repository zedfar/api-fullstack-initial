from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from datetime import datetime
from bson import ObjectId, errors as bson_errors
from app.database import get_mongodb
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/books", tags=["Books"])


def to_object_id(id_str: str):
    try:
        return ObjectId(id_str)
    except bson_errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

def book_helper(book) -> dict:
    return {
        "id": str(book["_id"]),
        "title": book["title"],
        "author": book["author"],
        "description": book.get("description"),
        "isbn": book.get("isbn"),
        "published_year": book.get("published_year"),
        "price": book.get("price"),
        "created_at": book["created_at"],
        "updated_at": book["updated_at"]
    }

@router.get("", response_model=List[BookResponse])
async def get_all_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    search: str = Query(None, description="Search by title or author"),
    author: str = Query(None, description="Filter by author"),
    min_price: float = Query(None, ge=0, description="Minimum price"),
    max_price: float = Query(None, ge=0, description="Maximum price"),
    db=Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    query = {}

    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"author": {"$regex": search, "$options": "i"}}
        ]

    if author:
        query["author"] = {"$regex": author, "$options": "i"}

    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price

    books = []
    async for book in db.books.find(query).skip(skip).limit(limit):
        books.append(book_helper(book))

    return books

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    db=Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    try:
        book = await db.books.find_one({"_id": to_object_id(book_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid book ID format"
        )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return book_helper(book)

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db=Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    book_dict = book_data.model_dump()
    book_dict["created_at"] = datetime.utcnow()
    book_dict["updated_at"] = datetime.utcnow()

    result = await db.books.insert_one(book_dict)
    new_book = await db.books.find_one({"_id": result.inserted_id})

    return book_helper(new_book)

@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    book_data: BookUpdate,
    db=Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    try:
        book = await db.books.find_one({"_id": to_object_id(book_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid book ID format"
        )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    update_data = book_data.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.books.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": update_data}
        )

    updated_book = await db.books.find_one({"_id": to_object_id(book_id)})
    return book_helper(updated_book)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    db=Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    try:
        result = await db.books.delete_one({"_id": to_object_id(book_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid book ID format"
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return None
