import abc

from domains.models.Book import Book

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

class AbstractBookRepository(abc.ABC):
    
    @abc.abstractmethod
    def add_book(self,book:Book)->Book:
        NotImplementedError
        
    @abc.abstractmethod
    def update_book(self,book:Book)-> Book:
        NotImplementedError
        
    @abc.abstractmethod
    def get_book_by_id(self,id:str)-> Book:
        NotImplementedError
        
    @abc.abstractmethod
    def delete_book_by_id(self,id:str)->bool:
        NotImplementedError
        
    @abc.abstractmethod
    def delete_book(self,book:Book)->bool:
        NotImplementedError
        
class BookRepository(AbstractBookRepository):
    def __init__(self,session:Session):
        super().__init__()
        self.session = session
    
    def add_book(self, book):
        self.session.add(book)
        self.session.commit()
        return book
    
    def update_book(self, book):
        existing_book = self.get_book_by_id(book.id)  # Assuming `id` is an attribute of Book
        if existing_book:
            existing_book = book
            # Add other attributes as needed
            self.session.commit()
            return existing_book
        raise ValueError("Book not found.")
    
    def get_book_by_id(self, id):
        book = self.session.query(Book).filter(Book.id == id).one_or_none()
        if book is None:
            raise NoResultFound("Book not found.")
        return book
    
    def delete_book_by_id(self, id: str) -> bool:
        try:
            book = self.get_book_by_id(id)
            self.session.delete(book)
            self.session.commit()
            return True  # Deletion was successful
        except NoResultFound:
            return False  # Book not found, deletion failed
    
    def delete_book(self, book: Book) -> bool:
        try:
            self.session.delete(book)
            self.session.commit()
            return True  # Deletion was successful
        except Exception as e:
            print(f"An error occurred: {e}")  # Optionally log the error
            return False  # An error occurred, deletion failed
    
    