from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models import DocumentDB
from app.models import DocumentCreate
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.repositories.processing_job_repository import (
    ProcessingJobRepository,
)


class DocumentService:

    @staticmethod
    async def create_document(
        session: AsyncSession,
        payload: DocumentCreate,
        correlation_id: str,
    ) -> DocumentDB:

        async with session.begin():

            document = await DocumentRepository.create(
                session=session,
                payload=payload,
            )

            await ProcessingJobRepository.create(
                session=session,
                document_id=document.document_id,
                correlation_id=correlation_id,
            )

        return document

    @staticmethod
    async def get_document(
        session: AsyncSession,
        document_id: int,
    ) -> DocumentDB | None:

        return await DocumentRepository.get_by_id(
            session=session,
            document_id=document_id,
        )
