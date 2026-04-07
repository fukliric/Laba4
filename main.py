from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import BookDB          # необходимо для создания таблиц (для метаданных)
from schemas import BookCreate, BookUpdate, BookResponse
from crud import (
    get_all_books,
    search_books_by_title,
    create_book,
    update_book,
    delete_book,
    get_book_by_id
)

# Создаём таблицы в БД (при первом запуске)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Book CRUD API (модульная структура)")

# 1. Получить все книги
@app.get("/books", response_model=list[BookResponse])
def read_all_books(db: Session = Depends(get_db)):
    return get_all_books(db)

# 2. Поиск по названию (частичное совпадение)
@app.get("/books/search", response_model=list[BookResponse])
def search_books(title: str, db: Session = Depends(get_db)):
    return search_books_by_title(db, title)

# 3. Создать новую книгу
@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    # Проверка дубликата по ISBN (если указан)
    if book.isbn:
        existing = db.query(BookDB).filter(BookDB.isbn == book.isbn).first()
        if existing:
            raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
    return create_book(db, book)

# 4. Обновить книгу по id
@app.put("/books/{book_id}", response_model=BookResponse)
def modify_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    updated = update_book(db, book_id, book_update)
    if updated is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated

# 5. Удалить книгу по id
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book(book_id: int, db: Session = Depends(get_db)):
    success = delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return