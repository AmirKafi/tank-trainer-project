import json
from datetime import date

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from config import QUEUE_NAMES
from domains.adapters.AbstractSqlAlchemyRepository import AbstractSqlAlchemyRepository
from domains.adapters.AuthorRepository import AuthorRepository
from domains.events.commands import CreateBookCommand
from domains.messaging.rabbitMQ_broker import RabbitMQBroker
from domains.models.BookManagementModels import Book
from services.UnitOfWork import UnitOfWork

message_queue = RabbitMQBroker('localhost')

def add_book(
        uow:UnitOfWork,
        repo:AbstractSqlAlchemyRepository,
        command:CreateBookCommand
):
    with uow:
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
                new_book.set_authors(author)
            except NoResultFound:
                raise HTTPException(status_code=404, detail=f"Author {author_id} not found")

        repo.add_book(new_book)
        uow.commit()