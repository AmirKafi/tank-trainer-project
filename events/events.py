from dataclasses import dataclass
from typing import Optional


class Event:
    pass

@dataclass
class SearchBooksEvent(Event):
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    genres: Optional[str] = None,
    city_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 10,
    sort_by_price: str = 'asc'