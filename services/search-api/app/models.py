from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

DocumentStatus = Literal[
    "received",
    "queued",
    "processing",
    "indexed",
    "failed",
]


class DocumentCreate(BaseModel):

    title: str = Field(
        min_length=3,
        max_length=200,
    )

    category: str = Field(
        min_length=2,
        max_length=50,
    )

    department: str | None = Field(
        default=None,
        max_length=100,
    )

    content: str = Field(
        min_length=10,
    )


class DocumentResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    document_id: int

    title: str

    category: str

    department: str | None

    status: DocumentStatus
