from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.database import build_engine, get_db
from app.db.init_db import init_db
from app.db.models import Task
from app.main import create_app
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import task_service


@pytest.fixture
def api(tmp_path, monkeypatch):
    forbidden = tmp_path / "development.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{forbidden}")
    engine = build_engine(f"sqlite:///{tmp_path}/test.db")
    init_db(engine)
    application = create_app(Settings(_env_file=None, debug=True))

    def override_db():
        with Session(engine) as session:
            yield session

    application.dependency_overrides[get_db] = override_db
    try:
        with TestClient(application) as client:
            yield client, engine
    finally:
        application.dependency_overrides.clear()
        engine.dispose()
        assert not forbidden.exists()


def test_create_list_persistence(api):
    client, engine = api
    assert client.get("/tasks").json() == []
    response = client.post(
        "/tasks",
        json={"title": " Review ", "description": "Notes", "due_date": "2026-12-01"},
    )
    assert response.status_code == 201
    task = response.json()
    assert task["title"] == "Review"
    assert task["priority"] == "medium"
    assert task["status"] == "pending"
    assert datetime.fromisoformat(task["created_at"]).utcoffset().total_seconds() == 0
    with Session(engine) as session:
        assert session.get(Task, task["id"]).description == "Notes"
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == [task]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": ""},
        {"title": "  "},
        {"title": "x", "priority": "urgent"},
        {"title": "x", "id": 1},
        {"title": "x", "due_date": "invalid"},
    ],
)
def test_create_validation(api, payload):
    client, _ = api
    assert client.post("/tasks", json=payload).status_code == 422
    assert client.get("/tasks").json() == []


def test_filters_order_pagination(api):
    client, engine = api
    with Session(engine) as session:
        for index in range(25):
            session.add(
                Task(
                    title=str(index),
                    created_at=datetime(2026, 1, 1, tzinfo=UTC),
                    status="completed" if index % 2 else "pending",
                    priority="high" if index % 3 else "low",
                )
            )
        session.commit()
    items = client.get("/tasks").json()
    assert len(items) == 20
    assert [item["id"] for item in items] == list(range(25, 5, -1))
    assert [item["id"] for item in client.get("/tasks?limit=2&offset=2").json()] == [
        23,
        22,
    ]
    assert client.get("/tasks?offset=100").json() == []
    for query, field, value in [
        ("status=completed", "status", "completed"),
        ("priority=low", "priority", "low"),
    ]:
        results = client.get("/tasks?" + query).json()
        assert results and all(item[field] == value for item in results)
    results = client.get("/tasks?status=pending&priority=high").json()
    assert results and all(
        item["status"] == "pending" and item["priority"] == "high" for item in results
    )
    assert client.get("/tasks?limit=100").status_code == 200
    # created_at takes precedence over a larger id.
    with Session(engine) as session:
        session.get(Task, 1).created_at = datetime(2030, 1, 1, tzinfo=UTC)
        session.commit()
    assert client.get("/tasks?limit=1").json()[0]["id"] == 1


@pytest.mark.parametrize(
    "query",
    ["limit=0", "limit=101", "offset=-1", "limit=abc", "status=bad", "priority=bad"],
)
def test_query_validation(api, query):
    assert api[0].get("/tasks?" + query).status_code == 422


def test_patch_partial_null_and_empty(api):
    client, engine = api
    task = client.post(
        "/tasks",
        json={
            "title": "Keep",
            "description": "Clear",
            "due_date": "2026-12-01",
            "priority": "high",
        },
    ).json()
    url = f"/tasks/{task['id']}"
    assert client.patch(url, json={}).json() == task
    response = client.patch(url, json={"status": "completed"})
    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "completed"
    for field in ("id", "title", "description", "due_date", "priority", "created_at"):
        assert updated[field] == task[field]
    assert updated["updated_at"] >= task["updated_at"]
    cleared = client.patch(url, json={"description": None, "due_date": None}).json()
    assert cleared["description"] is None and cleared["due_date"] is None
    with Session(engine) as session:
        assert session.get(Task, task["id"]).status == "completed"
    assert client.patch("/tasks/999", json={}).status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"title": None},
        {"title": " "},
        {"status": None},
        {"status": "bad"},
        {"priority": None},
        {"id": 2},
        {"created_at": "2020-01-01"},
        {"updated_at": "2020-01-01"},
    ],
)
def test_patch_validation(api, payload):
    client, _ = api
    task = client.post("/tasks", json={"title": "Keep"}).json()
    assert client.patch(f"/tasks/{task['id']}", json=payload).status_code == 422
    assert client.get("/tasks").json() == [task]


def test_health_openapi_and_cors(api):
    client, _ = api
    assert client.get("/health").status_code == 200
    assert client.get("/docs").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    assert set(paths["/tasks"]) == {"get", "post"}
    assert "201" in paths["/tasks"]["post"]["responses"]
    assert "patch" in paths["/tasks/{id}"]
    for origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
        response = client.options(
            "/tasks",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "PATCH",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
        assert "access-control-allow-credentials" not in response.headers
    assert (
        "access-control-allow-origin"
        not in client.get(
            "/tasks", headers={"Origin": "https://untrusted.example"}
        ).headers
    )


@pytest.mark.parametrize("operation", ["create", "update"])
def test_real_transaction_rollback_and_safe_error(api, operation):
    client, engine = api
    task = client.post("/tasks", json={"title": "Keep"}).json()
    event = "INSERT" if operation == "create" else "UPDATE"
    with engine.begin() as connection:
        connection.execute(
            text(
                f"CREATE TRIGGER reject_write BEFORE {event} ON tasks "
                "BEGIN SELECT RAISE(ABORT, 'private database detail'); END"
            )
        )
    with Session(engine) as session:
        with pytest.raises(IntegrityError):
            if operation == "create":
                task_service.create_task(session, TaskCreate(title="Rejected"))
            else:
                task_service.update_task(
                    session, task["id"], TaskUpdate(title="Rejected")
                )
        assert session.is_active
        assert session.scalar(select(Task)).title == "Keep"
    response = (
        client.post("/tasks", json={"title": "Rejected"})
        if operation == "create"
        else client.patch(f"/tasks/{task['id']}", json={"title": "Rejected"})
    )
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert client.get("/tasks").json() == [task]


def test_read_database_failure_is_sanitized(api):
    client, engine = api
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE tasks"))
    response = client.get("/tasks", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_environment(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", '["https://frontend.example"]')
    app = create_app(Settings(_env_file=None))
    with TestClient(app) as client:
        response = client.get("/health", headers={"Origin": "https://frontend.example"})
        assert (
            response.headers["access-control-allow-origin"]
            == "https://frontend.example"
        )


def test_apps_use_their_own_database_without_dependency_overrides(
    tmp_path, monkeypatch
):
    forbidden = tmp_path / "environment.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{forbidden}")
    paths = [tmp_path / "first.db", tmp_path / "second.db"]
    apps = []
    for path in paths:
        url = f"sqlite:///{path}"
        engine = build_engine(url)
        init_db(engine)
        engine.dispose()
        apps.append(create_app(Settings(_env_file=None, database_url=url)))
    with TestClient(apps[0]) as first, TestClient(apps[1]) as second:
        assert first.post("/tasks", json={"title": "First"}).status_code == 201
        assert second.get("/tasks").json() == []
        assert second.post("/tasks", json={"title": "Second"}).status_code == 201
        assert [task["title"] for task in first.get("/tasks").json()] == ["First"]
        assert [task["title"] for task in second.get("/tasks").json()] == ["Second"]
        assert (
            apps[0].state.session_factory.kw["bind"]
            is not apps[1].state.session_factory.kw["bind"]
        )
    for app in apps:
        assert not hasattr(app.state, "session_factory")
    # A new app lifetime reads the committed file, not another app's cached engine.
    with TestClient(apps[0]) as restarted:
        assert [task["title"] for task in restarted.get("/tasks").json()] == ["First"]
    assert not forbidden.exists()


@pytest.mark.parametrize(
    "offset, expected",
    [
        (9223372036854775807, 200),
        (9223372036854775808, 422),
        (10**100, 422),
    ],
)
def test_offset_sqlite_boundaries(api, offset, expected):
    response = api[0].get("/tasks", params={"offset": offset})
    assert response.status_code == expected
    if expected == 200:
        assert response.json() == []


@pytest.mark.parametrize("title", ["\x00task", "ta\x00sk", "task\x00"])
def test_nul_title_rejected_without_writes(api, title):
    client, _ = api
    task = client.post("/tasks", json={"title": "Keep"}).json()
    assert client.post("/tasks", json={"title": title}).status_code == 422
    assert (
        client.patch(f"/tasks/{task['id']}", json={"title": title}).status_code == 422
    )
    assert client.get("/tasks").json() == [task]
