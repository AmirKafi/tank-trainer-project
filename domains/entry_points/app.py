from typing import Union

from fastapi import FastAPI,requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domains.Events.commands import CreateBook
from domains.adapters.BookRepository import BookRepository
from domains.models.Book import Book
from services import config
from services.config import get_postgres_uri

get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
uri = get_postgres_uri()
engine = create_engine(uri)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print("Error connecting to the database:", e)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/Book",response_model=CreateBook)
def create_book(book: CreateBook):
    book = Book(
        title=book.title,
        genres= book.genres,
        publisher=book.publisher,
        release_date=book.release_date,
        price=book.price
    )
    book.set_authors(book.authors)

    repo = BookRepository(get_session())
    repo.add(book)
    return 200

