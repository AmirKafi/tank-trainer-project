import abc
from abc import abstractmethod

from Demos.win32ts_logoff_disconnected import session
from sqlalchemy.orm import Session

from domains.adapters.AbstractSqlAlchemyRepository import AbstractSqlAlchemyRepository
from domains.models.City import City


class AbstractCityRepository(abc.ABC):
    @abstractmethod
    def add_city(self, city)-> City:
        raise NotImplementedError

    @abstractmethod
    def get_city_list(self):
        raise NotImplementedError

    @abstractmethod
    def get_city_by_id(self, city_id)-> City:
        raise NotImplementedError


class CityRepository(AbstractSqlAlchemyRepository,AbstractCityRepository):
    def __init__(self, session: Session):
        super().__init__(session, City)

    def add_city(self, city)-> City:
        new_city = City(city.title)
        super().add(new_city)
        return new_city

    def get_city_list(self)->list[City]:
        cities=super().list()
        return cities

    def get_city_by_id(self, city_id)->City:
        city = super().get(city_id)
        return city
