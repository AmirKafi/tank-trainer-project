from datetime import datetime
from enum import Enum
from typing import List

from dateutil.relativedelta import relativedelta

from events import events
from events.events import Event


class City:
    id:int
    title:str

    def __init__(self, title: str):
        self.title = title

    def __str__(self):
        return self.title


class Author:
    id:int
    first_name:str
    last_name:str
    city:City

    def __init__(self, first_name: str, last_name: str, city: City):
        self.first_name = first_name
        self.last_name = last_name
        self.city = city

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def set_city(self, city: City):
        self.city = city



class ReservationStatus(Enum):
    RESERVED = 'Reserved'
    PENDING = 'Pending'

class Book:
    id: int
    title: str
    genres: str
    release_date: datetime
    isbn: str
    price: int
    status: ReservationStatus
    reservation_id: int = None
    authors: List[Author]
    version: int

    def __init__(self, title: str, genres: str, release_date: datetime, isbn: str, price: int):
        self.title = title
        self.genres = genres
        self.release_date = release_date
        self.isbn = isbn
        self.price = price
        self.status = ReservationStatus.PENDING
        self.authors = []
        self.events = []
        self.version = 0  # Initialize version here

    def update(self,title:str,genres:str,release_date:datetime,isbn:str,price:int):
        self.title = title
        self.genres = genres
        self.release_date = release_date
        self.isbn = isbn
        self.price = price
        self.authors = []


    def update_version(self):
        if self.version is None:
            self.version = 0

        self.version += 1

    def __str__(self):
        return f"Title: {self.title}, Genre: {self.genres}, Authors: {self.get_authors()}"

    def set_authors(self, authors: List[Author]):
        if not isinstance(authors, list):
            raise ValueError("Authors should be provided as a list")
        self.authors = authors  # Directly assign the authors list

    def get_author_ids(self):
        return [author.id for author in self.authors]

    def get_authors(self) -> str:
        if not self.authors:
            return "No authors assigned"
        return ', '.join(f"{author.first_name} {author.last_name}" for author in self.authors)

    def set_to_reserved(self, reservation_id: int):
        self.status = ReservationStatus.RESERVED
        self.reservation_id = reservation_id

    def add_event(self, event: Event):
        self.events.append(event)

class Reservation:
    id:int
    book_id :int
    member_id :int
    duration :int
    start_date :datetime
    end_date :datetime
    total_cost :int

    def __init__(self,book_id:int,member_id:int,duration:int):
        self.book_id = book_id
        self.member_id = member_id
        self.duration = duration
        self.start_date = datetime.now()
        self.end_date = datetime.now() + relativedelta(days=+ duration)
        self.total_cost = 0

    def set_total_cost(self, total_cost):
        self.total_cost = total_cost
