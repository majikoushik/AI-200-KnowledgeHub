from itertools import count
from threading import Lock

from app.models import DocumentCreate, DocumentResponse

# Temporary in-memory storage.
# PostgreSQL will replace this in Version 2.
_documents: dict[int, DocumentResponse] = {}

_id_counter = count(1)

_lock = Lock()


def create_document_record(
    document: DocumentCreate,
) -> DocumentResponse:

    with _lock:
        document_id = next(_id_counter)

        stored_document = DocumentResponse(
            document_id=document_id,
            title=document.title,
            category=document.category,
            department=document.department,
            status="received",
        )

        _documents[document_id] = stored_document

    return stored_document


def get_document_record(
    document_id: int,
) -> DocumentResponse | None:

    return _documents.get(document_id)
