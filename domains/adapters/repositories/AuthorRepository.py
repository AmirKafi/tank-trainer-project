import abc
from abc import abstractmethod

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from domains.adapters.repositories.AbstractSqlAlchemyRepository import AbstractSqlAlchemyRepository
from domains.adapters.repositories.CityRepository import CityRepository
from domains.models.BookManagementModels import Author


class AbstractAuthorRepository(abc.ABC):
    @abstractmethod
    def get_author_by_id(self, author_id)-> Author:
        raise NotImplementedError

    @abstractmethod
    def get_author_list(self)-> list[Author]:
        raise NotImplementedError



class AuthorRepository(AbstractSqlAlchemyRepository,AbstractAuthorRepository):
    def __init__(self,session:Session):
        super().__init__(session,Author)

    def get_author_by_id(self, author_id):
        author = super().get(author_id)
        if author is None:
            raise NoResultFound("Book not found.")
        return author

    def get_author_list(self):
        authors = super().list()
        for author in authors:
            city_repo = CityRepository(self.session)
            city = city_repo.get_city_by_id(author.city_id)
            author.set_city(city)

        return authors