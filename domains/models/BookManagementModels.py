import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Table, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import SQLALCHEMY_DATABASE_URL

# Create a declarative base class
Base = declarative_base()

# Define the association table for many-to-many relationship between Book and Author
metadata = Base.metadata

book_author_association = Table(
    'book_author_association',
    metadata,
    Column('book_id', UUID(as_uuid=True), ForeignKey('books.id'), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id'), primary_key=True)
)

class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    # Relationship with Author
    authors = relationship("Author", primaryjoin="City.id == Author.city_id", back_populates="city")

    def __init__(self, title: str):
        self.title = title

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)

    # Relationship with City
    city = relationship('City', back_populates='authors')
    books = relationship('Book', secondary=book_author_association, back_populates='authors')

    def __init__(self, first_name: str, last_name: str, city: City):
        self.first_name = first_name
        self.last_name = last_name
        self.city = city

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    @property
    def city_name(self) -> str:
        return self.city.title


class Book(Base):
    __tablename__ = 'books'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    genres = Column(String, nullable=False)
    release_date = Column(DateTime, nullable=False)
    isbn = Column(String, nullable=False, unique=True)
    price = Column(Integer, nullable=False)

    # Relationship with Author
    authors = relationship("Author", secondary=book_author_association, back_populates="books")

    def __init__(self, title: str, genres, release_date: datetime, isbn: str, price: int):
        self.id = uuid.uuid4()
        self.title = title
        self.genres = genres
        self.release_date = release_date
        self.isbn = isbn
        self.price = price
        self.authors = []

    def __str__(self):
        return f"Title of the book: {self.title} \nGenre: {self.genres} \nAuthors: {self.get_authors()}"

    def set_authors(self, author: Author):
        if not isinstance(author, Author):
            raise ValueError(f'{author} is not a valid Author')
        self.authors.append(author)

    def get_authors(self):
        return ', '.join(f"{author.first_name} {author.last_name}" for author in self.authors)
