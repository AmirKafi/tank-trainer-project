from datetime import date
from typing import Set
import uuid
from sqlalchemy import UUID, Column, Date, String,Integer
from sqlalchemy.orm import declarative_base
from domains.models.Author import Author

Base = declarative_base()

# Book is the aggregate root and has multiple authors
class Book(Base):
    __tablename__ = "Books"

    # Define columns
    id = Column("Id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _title = Column("Title", String, nullable=False)
    _genres = Column("Genres", String, nullable=False)
    _release_date = Column("ReleaseDate", Date, nullable=False)
    _publisher = Column("Publisher", String, nullable=False)
    _price = Column("Price", Integer, nullable=False)

    # Authors relationship; in practice, this would need an association table
    _authors: Set[Author] = set()  # Not mapped to database directly; manage with association table or manually


    def __init__(self,title:str,genres,release_date:date,publisher:str,price:int):
        self.id = uuid.uuid4()
        self._title = title
        self._genres = genres
        self._release_date = release_date
        self._publisher = publisher
        self._price = price
        self._authors = Set[Author] = set()

    def __eq__(self, other):
        if isinstance(other, Book):
            return self.id == other.id
        return False
    
    def __hash__(self):
        return hash(self.id)
    
    def __str__(self):
        return f"Title of the book : {self.title} \n Genre : {self.genres} \n Authors : {self.get_authors()}"


    def update(self,title:str,genres,release_date:date,publisher:str,price:int):
        self._title = title
        self._genres = genres
        self._release_date = release_date
        self._publisher = publisher
        self._price = price
        self._authors = Set[Author] = set()

    def set_authors(self,authors:list[Author]):
        for author in authors:
            if not isinstance(author, Author):
                raise ValueError(f'{author} is not a valid Author')
            self._authors.add(author)  # Add author to the set
    
    def get_authors(self):  
        # Returns joined authors names
        return ', '.join(f"{author.first_name} {author.last_name}" for author in self._authors)

            
    @property
    def title(self)->str:
        return self._title
    @property
    def genres(self)-> str:
        return self._genres
    @property
    def release_date(self)->date:
        return self._release_date
    @property
    def publisher(self)->str:
        return self._publisher
    @property
    def price(self)->int:
        return self._price
    @property
    def authors(self) -> Set[Author]:
        # Return the actual set of Author objects
        return self._authors
            
        
    
   