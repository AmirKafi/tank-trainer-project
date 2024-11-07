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
    id:str
    genres: str
    release_date: datetime
    isbn: str
    price: int
    author_ids:list[int]
