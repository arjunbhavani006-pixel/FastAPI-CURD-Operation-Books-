
from pathlib import Path
from typing import Optional
import re

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Book CRUD Manager")

# index.html nu location
BASE_DIR = Path(__file__).resolve().parent


# Validate Book Name and Author Name
def validate_text(value: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError("Invalid information: field cannot be empty")

    if not re.fullmatch(r"[A-Za-z ]+", value):
        raise ValueError(
            "Invalid information: only English letters and spaces are allowed"
        )

    return value


# Model for creating a book
class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    price: float = Field(ge=0)

    @field_validator("title", "author")
    @classmethod
    def check_text(cls, value):
        return validate_text(value)


# Model for updating a whole book or selected fields
class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    author: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, ge=0)

    @field_validator("title", "author")
    @classmethod
    def check_text(cls, value):
        if value is None:
            return value

        return validate_text(value)


# Temporary in-memory storage
books = {}
next_id = 1


# HOME: Open the frontend
@app.get("/")
def home():
    index_file = BASE_DIR / "index.html"

    if not index_file.exists():
        raise HTTPException(
            status_code=404,
            detail="index.html not found in project folder"
        )

    return FileResponse(index_file)


# CREATE: Add a new book
@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    global next_id

    new_book = {
        "id": next_id,
        "title": book.title,
        "author": book.author,
        "price": book.price
    }

    books[next_id] = new_book
    next_id += 1

    return {
        "message": "Book created successfully",
        "book": new_book
    }


# READ: Get all books
@app.get("/books")
def get_books():
    return list(books.values())


# READ: Get one book using its ID
@app.get("/books/{book_id}")
def get_book(book_id: int):
    if book_id not in books:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return books[book_id]


# PUT: Replace all book fields
@app.put("/books/{book_id}")
def replace_book(book_id: int, book: BookCreate):
    if book_id not in books:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    updated_book = {
        "id": book_id,
        "title": book.title,
        "author": book.author,
        "price": book.price
    }

    books[book_id] = updated_book

    return {
        "message": "Book replaced successfully",
        "book": updated_book
    }


# PATCH: Update only the fields supplied
@app.patch("/books/{book_id}")
def patch_book(book_id: int, book: BookUpdate):
    if book_id not in books:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    updated_fields = book.model_dump(exclude_unset=True)

    books[book_id].update(updated_fields)

    return {
        "message": "Book updated successfully",
        "book": books[book_id]
    }


# DELETE: Remove a book
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    if book_id not in books:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    deleted_book = books.pop(book_id)

    return {
        "message": "Book deleted successfully",
        "book": deleted_book
    }
