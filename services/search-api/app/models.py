from typing import Literal

from pydantic import BaseModel, Field


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
    document_id: int
    title: str
    category: str
    department: str | None
    status: Literal["received"]
