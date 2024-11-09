from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Table, create_engine, Enum
from sqlalchemy.orm import relationship, sessionmaker, registry

from config import SQLALCHEMY_DATABASE_URL
from domains.models.BookManagementModels import City, Author, Book, ReservationStatus, Reservation
from domains.models.MemberManagementModels import MembershipType, Member
from domains.models.PaymentModels import Payment

# Initialize a registry
mapper_registry = registry()

# Define the association table for many-to-many relationship between Book and Author
metadata = mapper_registry.metadata

book_author_association = Table(
    'book_author_association',
    metadata,
    Column('book_id', Integer, ForeignKey('books.id'), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id'), primary_key=True)
)

# Define tables
city_table = Table(
    'cities',
    metadata,
    Column('id', Integer, primary_key=True, index=True, autoincrement=True),
    Column('title', String, nullable=False)
)

author_table = Table(
    'authors',
    metadata,
    Column('id', Integer, primary_key=True, index=True, autoincrement=True),
    Column('first_name', String, nullable=False),
    Column('last_name', String, nullable=False),
    Column('city_id', Integer, ForeignKey('cities.id'), nullable=True)
)

book_table = Table(
    'books',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String, nullable=False),
    Column('genres', String, nullable=False),
    Column('release_date', DateTime, nullable=False),
    Column('isbn', String, nullable=False, unique=True),
    Column('price', Integer, nullable=False),
    Column('status', Enum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING)
)

reservation_table = Table(
    'reservations',
    metadata,
    Column("id", Integer, nullable=False, primary_key=True, autoincrement=True),
    Column("book_id", Integer, ForeignKey('books.id'), unique=True),  # Enforce one-to-one with unique=True
    Column("member_id", Integer, ForeignKey('members.id'), nullable=False),
    Column("start_date", DateTime, nullable=False),
    Column("end_date", DateTime, nullable=False),
    Column("total_cost", Integer, nullable=False),
    Column("version", Integer, default=1, nullable=False)
)


member_table = Table(
    'members',
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("phone_number", String, nullable=False),
    Column("membership_type", Enum(MembershipType), default=MembershipType.REGULAR),
    Column("membership_expiry", DateTime, nullable=True),
    Column("balance", Integer, nullable=True)
)

payment_table = Table(
    'payments',
    metadata,
Column("id", Integer, primary_key=True, autoincrement=True),
    Column("amount",Integer, nullable=False,default=0),
    Column("member_id", Integer, ForeignKey('members.id'), nullable=False),
    Column('payment_date',DateTime, nullable=False,default=datetime.now()),
)

# Initialize database and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
mapper_registry.metadata.create_all(engine)  # Ensure tables are created

Session = sessionmaker(bind=engine)
session = Session()

# Initialize tables and sample data
def init_db():
    db = Session()
    try:
        city_names = ["New York", "London", "Paris", "Tokyo", "Berlin"]
        author_names = [
            {"first_name": "Gabriel", "last_name": "Garcia Marquez"},
            {"first_name": "Haruki", "last_name": "Murakami"},
            {"first_name": "Jane", "last_name": "Austen"},
            {"first_name": "Leo", "last_name": "Tolstoy"},
            {"first_name": "Chinua", "last_name": "Achebe"},
        ]

        # Initialize cities
        cities = []
        for city_name in city_names:
            city = db.query(City).filter(City.title == city_name).first()
            if not city:
                city = City(title=city_name)
                db.add(city)
                db.commit()
                db.refresh(city)
                print(f"City '{city_name}' created.")
            cities.append(city)

        # Initialize authors
        for i, author_info in enumerate(author_names):
            city = cities[i % len(cities)]  # Assign each author a city, cycling if necessary
            author = db.query(Author).filter(
                Author.first_name == author_info["first_name"],
                Author.last_name == author_info["last_name"]
            ).first()
            if not author:
                author = Author(
                    first_name=author_info["first_name"],
                    last_name=author_info["last_name"],
                    city=city
                )
                db.add(author)
                db.commit()
                db.refresh(author)
                print(f"Author '{author_info['first_name']} {author_info['last_name']}' created in city '{city.title}'.")
    finally:
        db.close()

# Define the mapping manually
def start_mappers():

    mapper_registry.map_imperatively(
        Member,
        member_table,
        properties={
            'payments' : relationship(Payment, backref='member', cascade="all, delete-orphan"),
            'reservations':relationship(Reservation,back_populates='member')
        }
    )
    mapper_registry.map_imperatively(
        City,
        city_table,
        properties={
            'authors': relationship("Author", back_populates="city")
        }
    )

    mapper_registry.map_imperatively(
        Author,
        author_table,
        properties={
            'city': relationship(City, back_populates="authors"),
            'books': relationship("Book", secondary=book_author_association, back_populates="authors",default=list)
        }
    )

    mapper_registry.map_imperatively(
        Book,
        book_table,
        properties={
            'authors': relationship("Author", secondary=book_author_association, back_populates="books", default=list),
            'reservation': relationship("Reservation", back_populates="book", uselist=False)
        }
    )

    mapper_registry.map_imperatively(
        Payment,
        payment_table
    )

    mapper_registry.map_imperatively(
        Reservation,
        reservation_table,
        properties={
            'book': relationship(Book, back_populates="reservation", foreign_keys=[reservation_table.c.book_id]),
            'member':relationship(Member,back_populates='reservations')
        }
    )

    init_db()
