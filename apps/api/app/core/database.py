from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models so SQLAlchemy registers metadata before create_all.
    import app.api_keys.models  # noqa: F401
    import app.organizations.models  # noqa: F401
    import app.projects.models  # noqa: F401
    import app.usage.models  # noqa: F401
    import app.users.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
