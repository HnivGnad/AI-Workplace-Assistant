from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(session: Session, payload: TaskCreate) -> Task:
    try:
        task = Task(**payload.model_dump())
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except SQLAlchemyError:
        session.rollback()
        raise


def list_tasks(
    session: Session,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Task]:
    statement = select(Task)
    if status is not None:
        statement = statement.where(Task.status == status)
    if priority is not None:
        statement = statement.where(Task.priority == priority)
    statement = statement.order_by(Task.created_at.desc(), Task.id.desc())
    return list(session.scalars(statement.limit(limit).offset(offset)))


def update_task(session: Session, task_id: int, payload: TaskUpdate) -> Task | None:
    try:
        task = session.get(Task, task_id)
        if task is None:
            return None
        changes = payload.model_dump(exclude_unset=True)
        if not changes:
            return task
        for field, value in changes.items():
            setattr(task, field, value)
        session.commit()
        session.refresh(task)
        return task
    except SQLAlchemyError:
        session.rollback()
        raise
