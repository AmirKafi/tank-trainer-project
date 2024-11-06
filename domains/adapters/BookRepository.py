import abc
from abc import abstractmethod

from domains.adapters.AbstractSqlAlchemyRepository import AbstractSqlAlchemyRepository
from domains.adapters.AuthorRepository import AuthorRepository
from domains.models.Book import Book
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

class AbstractBookRepository(abc.ABC):

    @abstractmethod
    def get_book_list(self):
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

    def add_book(self, book):
        super().add(book)
        return book
    
    def update_book(self, book):
        existing_book = self.get_book_by_id(book.id)  # Assuming `id` is an attribute of Book
        if existing_book:
            existing_book.update(book.title,book.genres,book.release_date,book.publisher,book.price,book.authors)
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
    
    