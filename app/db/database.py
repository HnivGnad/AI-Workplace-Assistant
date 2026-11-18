from collections.abc import Generator
from pathlib import Path

from fastapi import Request
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


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


def get_db(request: Request) -> Generator[Session, None, None]:
    """Caller owns commit; errors and unfinished transactions roll back on close."""
    factory: sessionmaker[Session] = request.app.state.session_factory
    with factory() as session:
        yield session
