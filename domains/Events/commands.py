from dataclasses import dataclass
from datetime import date

from domains.models.Author import Author


class Command:
    pass

@dataclass
class CreateBook(Command):
    title:str
    genres:str
    release_date:date
    publisher:str
    price:int
    authors:list[Author]