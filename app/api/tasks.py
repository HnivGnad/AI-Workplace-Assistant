from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreate, session: DatabaseSession) -> Task:
    return task_service.create_task(session, payload)


@router.get("", response_model=list[TaskResponse], status_code=200)
def list_tasks(
    session: DatabaseSession,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=9223372036854775807)] = 0,
) -> list[Task]:
    return task_service.list_tasks(session, status, priority, limit, offset)


@router.patch(
    "/{id}",
    response_model=TaskResponse,
    status_code=200,
    responses={404: {"description": "Task not found"}},
)
def update_task(
    id: Annotated[int, Path(gt=0, le=9223372036854775807)],
    payload: TaskUpdate,
    session: DatabaseSession,
) -> Task:
    task = task_service.update_task(session, id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
