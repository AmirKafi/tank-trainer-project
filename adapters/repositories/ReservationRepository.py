from abc import abstractmethod,ABC

from sqlalchemy.orm import Session, joinedload

from adapters.repositories.AbstractSqlAlchemyRepository import AbstractSqlAlchemyRepository
from domains.models.BookManagementModels import Reservation


class AbstractReservationRepository(ABC):

    @abstractmethod
    def reserve(self,reservation:Reservation):
        raise NotImplementedError

    @abstractmethod
    def get_reserved_books(self,member_id):
        raise NotImplementedError


class ReservationRepository(AbstractSqlAlchemyRepository,AbstractReservationRepository):
    def __init__(self,session:Session):
        super().__init__(session,Reservation)
        self.seen = set[Reservation]

    def reserve(self,reservation:Reservation):
        super().add(reservation)
        return reservation

    def get_reserved_books(self,member_id):
        query = self.session.query(Reservation)
        reserved_books = query.options(joinedload(Reservation.member),joinedload(Reservation.book)).filter(Reservation.member_id == member_id).all()
        result = []

        for reserve in reserved_books:
            book = reserve.book
            # Now we can serialize the book with all the author data
            book_data = {
                "id": book.id,
                "title": book.title,
                "genres": book.genres,
                "isbn": book.isbn,
                "release_date": book.release_date,
                "price": book.price,
                "status": book.status,
                "authors": []  # Start with an empty list for authors
            }
            for author in book.authors:
                author_data = {
                    "id": author.id,
                    "first_name": author.first_name,
                    "last_name": author.last_name,
                    "city":{
                        "id":author.city.id,
                        "title":author.city.title
                    }
                }
                book_data["authors"].append(author_data)
            result.append(book_data)

        return result
