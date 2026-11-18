from sqlalchemy import Engine

from app.core.config import Settings
from app.db import models  # noqa: F401 -- register tables in metadata
from app.db.base import Base
from app.db.database import build_engine


def init_db(engine: Engine | None = None) -> None:
    """Create missing tables; this does not migrate existing tables."""
    if engine is not None:
        Base.metadata.create_all(engine)
        return
    owned_engine = build_engine(Settings().database_url)
    try:
        Base.metadata.create_all(owned_engine)
    finally:
        owned_engine.dispose()


if __name__ == "__main__":
    init_db()
