from domains.adapters.repositories.AuthorRepository import AuthorRepository
from services.UnitOfWork import UnitOfWork


def get_author_list_service(uow:UnitOfWork):
    with uow:
        repo = uow.get_repository(AuthorRepository)
        authors = repo.get_author_list()
        result = []
        for author in authors:
            city_data = {
                "id": author.id,
                "first_name": author.first_name,
                "last_name":author.last_name,
                "city":{
                    "id":author.city.id,
                    "title":author.city.title
                }
            }
            result.append(city_data)

        return result