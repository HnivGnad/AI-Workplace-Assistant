from datetime import date, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import CheckConstraint, Date, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UTCDateTime, utc_now


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DocumentStatus(StrEnum):
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


def enum_column(enum_type):
    return Enum(
        enum_type,
        values_callable=lambda values: [item.value for item in values],
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
    )


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "length(trim(title)) > 0 AND length(title) <= 255", name="task_title"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        enum_column(TaskStatus), default=TaskStatus.PENDING, server_default="pending"
    )
    priority: Mapped[TaskPriority] = mapped_column(
        enum_column(TaskPriority), default=TaskPriority.MEDIUM, server_default="medium"
    )
    due_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utc_now, onupdate=utc_now
    )


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("chunk_count >= 0", name="document_chunk_count"),
        CheckConstraint(
            "length(trim(filename)) > 0 AND length(filename) <= 255",
            name="document_filename",
        ),
        CheckConstraint(
            "length(trim(file_type)) > 0 AND length(file_type) <= 20",
            name="document_file_type",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(20))
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    status: Mapped[DocumentStatus] = mapped_column(
        enum_column(DocumentStatus),
        default=DocumentStatus.PROCESSING,
        server_default="processing",
    )
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utc_now)

    def __init__(self, **kwargs):
        kwargs.setdefault("id", str(uuid4()))
        super().__init__(**kwargs)
