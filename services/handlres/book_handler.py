import logging

from fastapi import HTTPException

from adapters.repositories.AuthorRepository import AuthorRepository
from adapters.repositories.BookRepository import BookRepository
from domains.models.BookManagementModels import Book
from events.commands import CreateBookCommand, UpdateBookCommand

from services.UnitOfWork import UnitOfWork

logger = logging.getLogger(__name__)

def add_book_handler(
        cmd: CreateBookCommand,
        uow: UnitOfWork()
):

    logger.debug(type(uow))
    with uow:
        repo = uow.get_repository(BookRepository)
        new_book = Book(
            title=cmd.title,
            genres=cmd.genres,
            release_date=cmd.release_date,
            isbn=cmd.isbn,
            price=cmd.price
        )
        author_repo = uow.get_repository(AuthorRepository)
        authors = []
        for author_id in cmd.author_ids:
            author = author_repo.get_author_by_id(author_id)
            if author is None:
                raise HTTPException(status_code=404, detail=f"Author {author_id} not found")
            authors.append(author)

        # Set all authors at once
        new_book.set_authors(authors)

        repo.add_book(new_book)
        uow.commit()


def update_book_handler(
        cmd:UpdateBookCommand
):
    with UnitOfWork() as uow:
        repo = uow.get_repository(BookRepository)
        book = repo.get_book_by_id(cmd.id)
        book.update(cmd.title, cmd.genres,cmd.release_date, cmd.isbn, cmd.price)
        author_repo = uow.get_repository(AuthorRepository)
        authors = []
        for author_id in cmd.author_ids:
            author = author_repo.get_author_by_id(author_id)
            if author is None:
                raise HTTPException(status_code=404, detail=f"Author {author_id} not found")
            authors.append(author)

        # Set all authors at once
        book.set_authors(authors)

        repo.update_book(book,cmd.id)