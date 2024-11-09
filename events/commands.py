from dataclasses import dataclass
from datetime import date, datetime


class Command:
    pass

@dataclass
class CreateBookCommand(Command):
    title:str
    genres:str
    release_date:datetime
    isbn:str
    price:int
    author_ids:list[int]

@dataclass
class UpdateBookCommand(Command):
    id:int
    genres: str
    release_date: datetime
    isbn: str
    price: int
    author_ids:list[int]

@dataclass
class CreateMemberCommand(Command):
    first_name:str
    last_name:str
    phone_number:str

@dataclass
class AddToMemberBalanceCommand(Command):
    amount:int

@dataclass
class ReserveBookCommand(Command):
    book_id:int
    duration:int
    