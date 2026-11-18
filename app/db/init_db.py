from sqlalchemy import Engine

from app.db import models  # noqa: F401 -- register tables in metadata
from app.db.base import Base
from app.db.database import get_engine


def init_db(engine: Engine | None = None) -> None:
    """Create missing tables; this does not migrate existing tables."""
    Base.metadata.create_all(engine if engine is not None else get_engine())


if __name__ == "__main__":
    init_db()
