from fastapi import HTTPException

from domains.adapters.repositories.AuthorRepository import AuthorRepository
from domains.adapters.repositories.BookRepository import BookRepository, logger
from events import CreateBookCommand
from events import SearchBooksEvent
from domains.models.BookManagementModels import Book
from services.UnitOfWork import UnitOfWork

def add_book_service(
        uow:UnitOfWork,
        command:CreateBookCommand
):
    with uow:
        repo = uow.get_repository(BookRepository)

        new_book = Book(
            title=command.title,
            genres=command.genres,
            release_date=command.release_date,
            isbn=command.isbn,
            price=command.price
        )

        author_repo = uow.get_repository(AuthorRepository)
        for author_id in command.author_ids:
            try:
                author = author_repo.get_author_by_id(author_id)
                new_book.set_authors([author])
            except Exception as e:
                logger.debug(e)
                raise HTTPException(status_code=404, detail=f"Author {author_id} not found")

        repo.add_book(new_book)
        uow.commit()

def get_book_list_filtered_service(
        uow:UnitOfWork,
        event:SearchBooksEvent
):
    with uow:
        repo = uow.get_repository(BookRepository)
        books = repo.get_book_list_filtered(
            event.search,
            event.min_price,
            event.max_price,
            event.genres,
            event.city_id,
            event.page,
            event.per_page,
            event.sort_by_price)
        return books