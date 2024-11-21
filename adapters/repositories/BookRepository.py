from abc import abstractmethod,ABC
from platform import version
from time import sleep
from typing import Optional, Set

from sqlalchemy import and_, update
from sqlalchemy.orm.exc import StaleDataError

from adapters.repositories.AbstractSqlAlchemyRepository import AbstractSqlAlchemyRepository
from domains.models.BookManagementModels import Author
from domains.models.BookManagementModels import Book
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.orm.attributes import set_committed_value

class AbstractBookRepository(ABC):

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

    @abstractmethod
    def add_book(self,book:Book)->Book:
        raise NotImplementedError
        
    @abstractmethod
    def update_book(self,book:Book,book_id:int)-> Book:
        raise NotImplementedError
        
    @abstractmethod
    def get_book_by_id(self,id:int)-> Book:
        raise NotImplementedError
        
    @abstractmethod
    def delete_book_by_id(self,id:int)->bool:
        raise NotImplementedError
        
    @abstractmethod
    def delete_book(self,book:Book)->bool:
        raise NotImplementedError

    @abstractmethod
    def set_to_reserved(self,book:Book,reservation_id:int):
        raise NotImplementedError
        
class BookRepository(AbstractSqlAlchemyRepository,AbstractBookRepository):
    def __init__(self,session:Session):
        self.seen = set()  # type: Set[Book]
        self.session = session
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

        filters = []

        # Collect filter conditions
        if search:
            filters.append(Book.title.ilike(f"%{search}%"))
        if min_price is not None:
            filters.append(Book.price >= min_price)
        if max_price is not None:
            filters.append(Book.price <= max_price)
        if genres is not None:
            filters.append(Book.genres.ilike(f"%{genres}%"))
        if city_id is not None:
            filters.append(Author.city_id == city_id)

        # Sorting
        sort_order = Book.price.asc() if sort_by_price == 'asc' else Book.price.desc()

        books = (self.session
                 .query(Book)
                 .options(joinedload(Book.authors)
                          .joinedload(Author.city))
                 .filter(and_(*filters))
                 .order_by(sort_order)
                 .offset((page-1)*per_page)).all()

        result = []
        for book in books:
            book_data = {
                "id": book.id,
                "title": book.title,
                "genres": book.genres,
                "isbn": book.isbn,
                "release_date": book.release_date,
                "price": book.price,
                "status":book.status.value,
                "authors": []  # Start with an empty list for authors
            }

            # Iterate over the authors and serialize their data
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

    def add_book(self, book):
        super().add(book)
        self.seen.add(book)
        return book

    def update_book(self, book, book_id):
        # Step 1: Retrieve the existing book by ID for version control and update
        existing_book = self.get_book_by_id(book_id)

        # Log version information for debugging
        print(f"Existing version: {existing_book.version}, Book version: {book.version}")

        # Step 2: Update scalar fields only
        stmt = (
            update(Book)
            .where(and_(Book.id == book_id, Book.version == existing_book.version))
            .values(
                title=book.title,
                genres=book.genres,
                release_date=book.release_date,
                isbn=book.isbn,
                price=book.price,
                version=existing_book.version
            )
        )
        print(str(stmt.compile(compile_kwargs={"literal_binds": True})))
        print(f"Executing update with: {stmt}")

        result = super().execute(stmt)

        # Check for stale data
        if result.rowcount == 0:
            raise StaleDataError("The book has been modified by another transaction.")

        # Step 3: Update authors relationship
        # Directly assign the authors list to the existing_book's authors relationship
        existing_book.authors = book.authors

        # Commit the session to save changes in both scalar fields and relationships
        self.session.flush()  # Flush pending changes to the database
        self.session.refresh(existing_book)  # Refresh to reflect the new state
        self.session.commit()

        # Optional: Print for confirmation
        print("Book updated successfully with new authors and version.")

    def get_book_by_id(self, id:int):
        book = super().get(id)
        if book is None:
            raise NoResultFound("Book not found.")
        return book
    
    def delete_book_by_id(self, id: int) -> bool:
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

    def set_to_reserved(self, book:Book,reservation_id:int):
        book.set_to_reserved(reservation_id)
        existing_book = self.get_book_by_id(book.id)
        stmt = (
            update(Book)
            .where(and_(Book.version == existing_book.version))
            .values(
                status=book.status,
                version=book.version+1 )
        )
        result = super().execute(stmt)
        if not result:
            raise StaleDataError("The book has been modified by another transaction.")
        super().add(book)
    
    