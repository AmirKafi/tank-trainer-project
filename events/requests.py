from pydantic import BaseModel
from typing import Optional


class ReserveBookRequest(BaseModel):
    book_id:int
    duration:int


class SearchBooksRequest(BaseModel):
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    genres: Optional[str] = None,
    city_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 10,
    sort_by_price: str = 'asc'