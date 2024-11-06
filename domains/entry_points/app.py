import logging

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from typing import List

from sqlalchemy.orm import sessionmaker

from domains.adapters.AuthorRepository import AuthorRepository
from domains.adapters.BookRepository import BookRepository
from domains.events.commands import CreateBookCommand
from domains.models.Book import Book
from uuid import UUID

from services.UnitOfWork import UnitOfWork
from services.config import SQLALCHEMY_DATABASE_URL

app = FastAPI()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI's async support
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger = logging.getLogger("uvicorn.error")  # FastAPI integrates well with uvicorn's logging
logger.setLevel(logging.DEBUG)

@app.post("/books", response_model=CreateBookCommand)
async def create_book(request: CreateBookCommand):
    # Convert genres list to a comma-separated string
    logger.log(logging.INFO,"In the endpoint")

    session = SessionLocal()
    logger.log(logging.INFO,str(session))
    with UnitOfWork(session) as uow:
        book_repo = uow.get_repository(BookRepository)

        # Create Book instance with initial values
        new_book = Book(
            title=request.title,
            genres=request.genres,
            release_date=request.release_date,
            publisher=request.publisher,
            price=request.price
        )

        # Optionally fetch authors from database if author validation is needed
        author_repo = uow.get_repository(AuthorRepository)
        for author_id in request.author_ids:
            try:
                author = author_repo.get_author_by_id(UUID(author_id))
                new_book.set_authors([author])
            except NoResultFound:
                raise HTTPException(status_code=404, detail=f"Author {author_id} not found")

        # Add and commit the book to the database
        book_repo.add_book(new_book)
        uow.commit()

    return request
