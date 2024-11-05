
from sqlalchemy import UUID, Column, String
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

# For easier searching City must be an Entity
class City(Base):
    __tablename__ = 'Cities'

    _id = Column("Id",UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    _title = Column("Title",String, nullable=False)

    def __repr__(self):
        return f"<City(name={self.name})>"

    def __init__(self,title:str):
        self._id = uuid.uuid4()
        self._title = title

    def __eq__(self, other):
        if isinstance(other, City):
            return self._id == other._id
        return False

    def __hash__(self):
        return hash(self._id)

    def __str__(self):
        return self._title

    @property
    def title(self) -> str:
        return self.title