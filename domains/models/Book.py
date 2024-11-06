import uuid
from datetime import date
from typing import Set

from domains.models.Author import Author


# Book is the aggregate root and has multiple authors
class Book:

    def __init__(self,title:str,genres,release_date:date,publisher:str,price:int):
        self.id = uuid.uuid4()
        self.title = title
        self.genres = genres
        self.release_date = release_date
        self.publisher = publisher
        self.price = price
        self.authors = []

    def __eq__(self, other):
        if isinstance(other, Book):
            return self.id == other.id
        return False
    
    def __hash__(self):
        return hash(self.id)
    
    def __str__(self):
        return f"Title of the book : {self.title} \n Genre : {self.genres} \n Authors : {self.get_authors()}"


    def update(self,title:str,genres,release_date:date,publisher:str,price:int,authors:list[Author]):
        self.title = title
        self.genres = genres
        self.release_date = release_date
        self.publisher = publisher
        self.price = price
        self.authors = authors

    def set_authors(self,author:Author):
        if not isinstance(author, Author):
            raise ValueError(f'{author} is not a valid Author')
        self.authors.append(author) # Add author to the set
    
    def get_authors(self):  
        # Returns joined authors names
        return ', '.join(f"{author.first_name} {author.last_name}" for author in self._authors)
            
        
    
   