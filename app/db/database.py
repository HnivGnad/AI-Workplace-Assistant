from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings


def build_engine(database_url: str) -> Engine:
    url = make_url(database_url)
    if url.get_backend_name() != "sqlite":
        raise ValueError("Only SQLite is supported in this phase")
    options = {"connect_args": {"check_same_thread": False}}
    if url.database in (None, "", ":memory:"):
        options["poolclass"] = StaticPool
    else:
        Path(url.database).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(url, **options)


@lru_cache
def get_engine() -> Engine:
    return build_engine(Settings().database_url)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Caller owns commit; errors and unfinished transactions roll back on close."""
    with get_session_factory()() as session:
        yield session
