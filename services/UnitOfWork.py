from abc import ABC, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import SQLALCHEMY_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,            # Maximum number of connections in the pool
    max_overflow=20,         # Additional connections allowed beyond pool_size
    pool_timeout=30,         # Timeout for retrieving a connection from the pool
    pool_recycle=1800,       # Time after which to recycle the connection
)
session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class AbstractUnitOfWork(ABC):
    @abstractmethod
    def get_repository(self,repo_class):
        raise NotImplementedError

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abstractmethod
    def collect_new_events(self):
        raise NotImplementedError


class UnitOfWork:
    def __init__(self):
        self.session = session_maker()
        self.repositories = {}
        self.events = []

    def get_repository(self, repo_class):
        if repo_class not in self.repositories:
            self.repositories[repo_class] = repo_class(self.session)
        return self.repositories[repo_class]

    def collect_new_events(self):
        # Assuming each entity has events to be collected
        for repo in self.repositories.values():
            if repo.seen is not None:
                for entity in repo.seen:
                    events_attr = getattr(entity, "events", False)
                    if events_attr is not False:
                        while entity.events:
                            yield entity.events.pop(0)

    def commit(self):
        self.session.commit()
        self.collect_new_events()  # Collect events after commit

    def rollback(self):
        self.session.rollback()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.session.close()

