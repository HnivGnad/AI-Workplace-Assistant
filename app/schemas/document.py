from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.db.models import DocumentStatus


class DocumentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
    ]
    file_type: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)
    ]


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    file_type: str
    chunk_count: int = Field(ge=0)
    status: DocumentStatus
    created_at: datetime
