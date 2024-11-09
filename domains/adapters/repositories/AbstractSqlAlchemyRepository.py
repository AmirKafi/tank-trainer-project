from sqlalchemy.orm import Session, declarative_base

from typing import Type, TypeVar, Generic, Optional
from sqlalchemy.orm import Session

Base = declarative_base()
T = TypeVar('T')

class AbstractSqlAlchemyRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model  # The model to work with (e.g., Book, Author)

    def add(self, entity: T) -> None:
        self.session.add(entity)
        self.session.commit()

    def remove(self, entity: T) -> None:
        self.session.delete(entity)
        self.session.commit()

    def get(self, entity_id) -> Optional[T]:
        return self.session.get(self.model, entity_id)

    def list(self) -> list[T]:
        return self.session.query(self.model).all()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()