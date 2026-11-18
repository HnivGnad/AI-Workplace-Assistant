from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.db import database
from app.db.init_db import init_db
from app.db.models import Document, Task
from app.schemas.document import DocumentCreate, DocumentResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate


@pytest.fixture
def engine(tmp_path):
    engine = database.build_engine(f"sqlite:///{tmp_path}/nested/test.db")
    init_db(engine)
    yield engine
    engine.dispose()


def test_task_roundtrip_and_update(engine):
    with Session(engine) as session:
        task = Task(**TaskCreate(title=" Review report ").model_dump())
        session.add(task)
        session.commit()
        session.refresh(task)
        response = TaskResponse.model_validate(task)
        assert response.title == "Review report"
        assert response.status == "pending"
        assert response.priority == "medium"
        assert response.created_at.tzinfo == UTC
        assert response.updated_at.tzinfo == UTC
        task.updated_at = datetime(2000, 1, 1, tzinfo=UTC)
        session.commit()
        task.title = "Reviewed"
        session.commit()
        session.refresh(task)
        assert task.updated_at > datetime(2000, 1, 1, tzinfo=UTC)
        assert task.created_at == response.created_at
    with Session(engine) as session:
        assert session.scalar(select(Task)).title == "Reviewed"
        assert session.execute(text("SELECT status FROM tasks")).scalar() == "pending"


def test_document_roundtrip(engine):
    document = Document(
        **DocumentCreate(filename="report.pdf", file_type="pdf").model_dump()
    )
    assert UUID(document.id).version == 4
    assert Document(filename="other.txt", file_type="txt").id != document.id
    with Session(engine) as session:
        session.add(document)
        session.commit()
        session.refresh(document)
        response = DocumentResponse.model_validate(document)
        assert response.status == "processing"
        assert response.chunk_count == 0
        assert response.created_at.tzinfo == UTC


@pytest.mark.parametrize("title", ["", "   ", "\t\n", "a" * 256, None])
def test_invalid_title(title):
    with pytest.raises(ValidationError):
        TaskCreate(title=title)


@pytest.mark.parametrize(
    "payload",
    [
        {"status": "unknown"},
        {"priority": "urgent"},
        {"title": None},
        {"status": None},
        {"priority": None},
        {"id": 3},
        {"created_at": "2020-01-01"},
        {"updated_at": "2020-01-01"},
    ],
)
def test_invalid_update(payload):
    with pytest.raises(ValidationError):
        TaskUpdate(**payload)


def test_partial_update():
    assert TaskUpdate().model_dump(exclude_unset=True) == {}
    assert TaskUpdate(description=None).model_dump(exclude_unset=True) == {
        "description": None
    }
    assert TaskUpdate(status="completed").model_dump(exclude_unset=True) == {
        "status": "completed"
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"filename": "", "file_type": "pdf"},
        {"filename": "ok", "file_type": "x" * 21},
        {"filename": "ok", "file_type": "txt", "id": "forbidden"},
    ],
)
def test_invalid_document(payload):
    with pytest.raises(ValidationError):
        DocumentCreate(**payload)


def test_schema_and_repeat_initialization(engine):
    with Session(engine) as session:
        session.add(Task(title="Retain me"))
        session.commit()
    init_db(engine)
    assert set(inspect(engine).get_table_names()) == {"tasks", "documents"}
    with Session(engine) as session:
        assert session.scalar(select(Task)).title == "Retain me"
        with pytest.raises(IntegrityError):
            session.execute(text("UPDATE tasks SET status = 'invalid'"))
        session.rollback()


def test_dependency_closes_and_rolls_back(engine, monkeypatch):
    class TrackedSession(Session):
        closed = False

        def close(self):
            self.closed = True
            super().close()

    factory = sessionmaker(engine, class_=TrackedSession)
    monkeypatch.setattr(database, "get_session_factory", lambda: factory)
    dependency = database.get_db()
    session = next(dependency)
    session.add(Task(title="Uncommitted"))
    session.flush()
    dependency.close()
    assert session.closed
    with factory() as check:
        assert check.scalar(select(Task)) is None


def test_import_has_no_database_side_effects(tmp_path):
    import os
    import subprocess
    import sys

    path = tmp_path / "untouched" / "app.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{path}"}
    subprocess.run(
        [sys.executable, "-c", "import app.db.database; import app.db.init_db"],
        env=env,
        check=True,
        timeout=15,
    )
    assert not path.parent.exists()
