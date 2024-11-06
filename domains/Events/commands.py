from dataclasses import dataclass
from datetime import date

from domains.models.Author import Author


class Command:
    pass

@dataclass
class CreateBookCommand(Command):
    title:str
    genres:str
    release_date:date
    publisher:str
    price:int
    author_ids:list[str]

@dataclass
class UpdateBookCommand(Command):
    id:str
    genres: str
    release_date: date
    publisher: str
    price: int
    author_ids:list[str]
