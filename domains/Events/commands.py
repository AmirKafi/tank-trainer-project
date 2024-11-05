from dataclasses import dataclass
from datetime import date


class Command:
    pass

@dataclass
class CreateBook(Command):
    title:str
    genres:str
    release_date:date
    publisher:str
    price:int