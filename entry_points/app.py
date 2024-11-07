import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound

from sqlalchemy.orm import sessionmaker

from domains.adapters import table_mapping
from domains.adapters.AuthorRepository import AuthorRepository
from domains.adapters.BookRepository import BookRepository
from domains.adapters.CityRepository import CityRepository
from domains.adapters.table_mapping import init_db
from domains.events.commands import CreateBookCommand
from domains.messaging.rabbitMQ_broker import RabbitMQBroker
from domains.models.BookManagementModels import Book
from services.BookService import add_book

from services.UnitOfWork import UnitOfWork
from config import SQLALCHEMY_DATABASE_URL


app = FastAPI()

broker = RabbitMQBroker()

engine = table_mapping.start_mappers()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#init_db(SessionLocal())

logger = logging.getLogger("uvicorn.error")  # FastAPI integrates well with uvicorn logging
logger.setLevel(logging.DEBUG)

@app.get("/City/get_list")
def get_city_list():
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                city_repo = uow.get_repository(CityRepository)
                city_list = city_repo.get_city_list()
                return jsonable_encoder(city_list)
    except Exception as e:
        logger.error(f"Error retrieving Cities: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving Cities {e}")

@app.get("/Author/get_list")
def get_author_list():
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                author_repo = uow.get_repository(AuthorRepository)
                author_list = author_repo.get_author_list()
                return jsonable_encoder(author_list)
    except Exception as e:
        logger.debug(f"Error retrieving authors: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving authors")

@app.get("/books/get_list")
def get_book_list(
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        genres: Optional[str] = None,
        city_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 10,
        sort_by_price: str = 'asc'
):
    book_repo = BookRepository(SessionLocal())
    books = book_repo.get_book_list_filtered(search, min_price, max_price, genres, city_id, page, per_page, sort_by_price)
    return {"books": books}

@app.post("/books", response_model=CreateBookCommand)
def create_book(request: CreateBookCommand):
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                book_repo = uow.get_repository(BookRepository)
                add_book(uow,book_repo,request)
                return request
    except Exception as e:
        logger.error(f"Error creating book: {e}")
        raise HTTPException(status_code=500, detail="Error creating book")

