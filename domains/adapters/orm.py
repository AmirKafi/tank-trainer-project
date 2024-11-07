import uuid
from sqlalchemy import Table, MetaData, Column, String, Date, ForeignKey, create_engine,Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID  # Use UUID from PostgreSQL dialect for UUID support
from sqlalchemy.orm import relationship, registry

from domains.models.Author import Author
from domains.models.City import City
from domains.models.Book import Book
from services.config import SQLALCHEMY_DATABASE_URL

# Initialize registry and metadata
metadata = MetaData()
mapper_registry = registry()
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI's async support
)

# Define the tables
city = Table(
    'City',
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String, nullable=False)
)

author = Table(
    'Author',
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("city_id", Integer, ForeignKey("City.id"), nullable=False)
)

book = Table(
    'Book',
    metadata,
    Column("id", PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("title", String, nullable=False),
    Column("genres", String, nullable=False),
    Column("release_date", Date, nullable=False),
    Column("publisher", String, nullable=False),
    Column("price", Integer, nullable=False)
)

book_author_association = Table(
    "book_author_association",
    metadata,
    Column("book_id", PGUUID(as_uuid=True), ForeignKey("Book.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("Author.id"), primary_key=True)
)

# Define the mappings
def start_mappers():
    mapper_registry.map_imperatively(
        City,
        city,
        properties={
            "authors": relationship("Author", back_populates="city")
        }
    )

    mapper_registry.map_imperatively(
        Author,
        author,
        properties={
            "city": relationship("City", back_populates="authors"),
            "books": relationship("Book", secondary=book_author_association, back_populates="authors")
        }
    )

    mapper_registry.map_imperatively(
        Book,
        book,
        properties={
            "authors": relationship("Author", secondary=book_author_association, back_populates="books")
        }
    )

    metadata.create_all(engine)
