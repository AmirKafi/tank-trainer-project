from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from services import config

DEFAULT_SESSION = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
        isolation_level="REPEATABLE READ",
    )
)


class UnitOfWork:

    def __init__(self, session: Session = DEFAULT_SESSION):
        self.session = session
        self.repositories = {}

    def get_repository(self, repo_class):
        if repo_class not in self.repositories:
            self.repositories[repo_class] = repo_class(self.session)
        return self.repositories[repo_class]

    def commit(self):
        self.session.commit()

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
