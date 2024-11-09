from domains.adapters.repositories.CityRepository import CityRepository
from services.UnitOfWork import UnitOfWork


def get_city_list_service(uow:UnitOfWork):
    with uow:
        repo = uow.get_repository(CityRepository)
        cities = repo.get_city_list()

        result = []
        for city in cities:
            city_data = {
                "id": city.id,
                "title": city.title
            }
            result.append(city_data)

        return result