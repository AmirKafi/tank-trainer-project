import logging

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound

from sqlalchemy.orm import sessionmaker

from domains.adapters import orm
from domains.adapters.AuthorRepository import AuthorRepository
from domains.adapters.BookRepository import BookRepository
from domains.adapters.CityRepository import CityRepository
from domains.events.commands import CreateBookCommand
from domains.models.Book import Book

from services.UnitOfWork import UnitOfWork
from services.config import SQLALCHEMY_DATABASE_URL

orm.start_mappers()
app = FastAPI()

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI async support
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


logger = logging.getLogger("uvicorn.error")  # FastAPI integrates well with uvicorn logging
logger.setLevel(logging.DEBUG)

@app.get("/")
def read_root():
    pass

@app.get("/City/get_list")
def get_city_list():
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                city_repo = uow.get_repository(CityRepository)
                city_list = city_repo.get_city_list()
                logger.debug(f"Cities list retrieved successfully => {city_list}")
                return jsonable_encoder(city_list)
    except Exception as e:
        logger.error(f"Error retrieving Cities: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving Cities {e}")

@app.get("/Author/get_list")
def get_author_list():
    logger.debug("Attempting to fetch author list")
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                author_repo = uow.get_repository(AuthorRepository)
                author_list = author_repo.get_author_list()
                logger.debug("Author list retrieved successfully")
                return jsonable_encoder(author_list)
    except Exception as e:
        logger.error(f"Error retrieving authors: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving authors")


@app.get("/Book/get_list")
def get_book_list():
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                book_repo = uow.get_repository(BookRepository)
                book_list = book_repo.get_book_list()
                logger.debug("book list retrieved successfully")
                return jsonable_encoder(book_list)
    except Exception as e:
        logger.error(f"Error retrieving books: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving books")
    
@app.post("/books", response_model=CreateBookCommand)
def create_book(request: CreateBookCommand):
    logger.info("In the /books endpoint")
    try:
        with SessionLocal() as session:
            with UnitOfWork(session) as uow:
                book_repo = uow.get_repository(BookRepository)

                new_book = Book(
                    title=request.title,
                    genres=request.genres,
                    release_date=request.release_date,
                    publisher=request.publisher,
                    price=request.price
                )

                author_repo = uow.get_repository(AuthorRepository)
                for author_id in request.author_ids:
                    try:
                        author = author_repo.get_author_by_id(author_id)
                        new_book.set_authors(author)
                    except NoResultFound:
                        logger.warning(f"Author {author_id} not found")
                        raise HTTPException(status_code=404, detail=f"Author {author_id} not found")

                book_repo.add_book(new_book)
                uow.commit()
                logger.info("New book created successfully")
                return request
    except Exception as e:
        logger.error(f"Error creating book: {e}")
        raise HTTPException(status_code=500, detail="Error creating book")

