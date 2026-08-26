from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models import DocumentDB
from app.models import DocumentCreate


class DocumentRepository:

    @staticmethod
    async def create(
        session: AsyncSession,
        payload: DocumentCreate,
    ) -> DocumentDB:

        document = DocumentDB(
            title=payload.title,
            category=payload.category,
            department=payload.department,
            content=payload.content,
            status="received",
        )

        session.add(document)

        # Executes INSERT without committing.
        # We need the generated document_id.
        await session.flush()

        return document

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        document_id: int,
    ) -> DocumentDB | None:

        return await session.get(
            DocumentDB,
            document_id,
        )
