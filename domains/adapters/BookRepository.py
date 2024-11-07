import abc
from abc import abstractmethod
from typing import Optional

from domains.adapters.AbstractSqlAlchemyRepository import AbstractSqlAlchemyRepository
from domains.adapters.CityRepository import CityRepository
from domains.models.BookManagementModels import Author
from domains.models.BookManagementModels import Book
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload


class AbstractBookRepository(abc.ABC):

    @abstractmethod
    def get_book_list(self):
        raise NotImplementedError

    @abstractmethod
    def get_book_list_filtered(self,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        genres: Optional[str] = None,
        city_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 10,
        sort_by_price: str = 'asc'):
        raise NotImplementedError

    @abc.abstractmethod
    def add_book(self,book:Book)->Book:
        raise NotImplementedError
        
    @abc.abstractmethod
    def update_book(self,book:Book)-> Book:
        raise NotImplementedError
        
    @abc.abstractmethod
    def get_book_by_id(self,id:str)-> Book:
        raise NotImplementedError
        
    @abc.abstractmethod
    def delete_book_by_id(self,id:str)->bool:
        raise NotImplementedError
        
    @abc.abstractmethod
    def delete_book(self,book:Book)->bool:
        raise NotImplementedError
        
class BookRepository(AbstractSqlAlchemyRepository,AbstractBookRepository):
    def __init__(self,session:Session):
        super().__init__(session,Book)

    def get_book_list(self):
        books = super().list()
        return books

    def get_book_list_filtered(self,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        genres: Optional[str] = None,
        city_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 10,
        sort_by_price: str = 'asc'):

        query = self.session.query(Book)

        # Filtering conditions
        if search:
            query = query.filter(
                (Book.title.ilike(f"%{search}%"))
            )
        if min_price is not None:
            query = query.filter(Book.price >= min_price)
        if max_price is not None:
            query = query.filter(Book.price <= max_price)
        if genres is not None:
            query = query.filter(Book.genres == genres)
        if city_id is not None:
            query = query.options(joinedload(Book.authors).joinedload(Author.city))
            query = query.filter(Author.city_id == city_id)

        # Sorting
        sort_order = Book.price.asc() if sort_by_price == 'asc' else Book.price.desc()
        query = query.order_by(sort_order)

        books = query.options(joinedload(Book.authors).joinedload(Author.city)).offset((page - 1) * per_page).limit(per_page).all()
        result = []

        for book in books:
            # Now we can serialize the book with all the author data
            book_data = {
                "id": book.id,
                "title": book.title,
                "genres": book.genres,
                "isbn": book.isbn,
                "release_date": book.release_date,
                "price": book.price,
                "authors": book.authors  # Add the list of authors
            }

            result.append(book_data)
        # Pagination

        return {"books": result}

    def add_book(self, book):
        super().add(book)
        return book
    
    def update_book(self, book):
        existing_book = self.get_book_by_id(book.id)  # Assuming `id` is an attribute of Book
        if existing_book:
            existing_book.update(book.title,book.genres,book.release_date,book.isbn,book.price,book.authors)
            self.session.add(existing_book)
            return existing_book
        raise ValueError("Book not found.")
    
    def get_book_by_id(self, id:str):
        book = super().get(id)
        if book is None:
            raise NoResultFound("Book not found.")
        return book
    
    def delete_book_by_id(self, id: str) -> bool:
        try:
            book = self.get_book_by_id(id)
            super().remove(book)
            return True  # Deletion was successful
        except NoResultFound:
            return False  # Book not found, deletion failed
    
    def delete_book(self, book: Book) -> bool:
        try:
            super().remove(book)
            return True  # Deletion was successful
        except Exception as e:
            print(f"An error occurred: {e}")  # Optionally log the error
            return False  # An error occurred, deletion failed
    
    