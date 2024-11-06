import abc
from abc import abstractmethod

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from domains.adapters.AbstractSqlAlchemyRepository import AbstractSqlAlchemyRepository
from domains.models.Author import Author


class AbstractAuthorRepository(abc.ABC):
    @abstractmethod
    def get_author_by_id(self, author_id):
        raise NotImplementedError



class AuthorRepository(AbstractSqlAlchemyRepository,AbstractAuthorRepository):
    def __init__(self,session:Session):
        super().__init__(session,Author)

    def get_author_by_id(self, author_id):
        author = super().get(author_id)
        if author is None:
            raise NoResultFound("Book not found.")
        return author