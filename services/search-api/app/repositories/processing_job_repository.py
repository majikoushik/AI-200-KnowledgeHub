from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models import ProcessingJobDB


class ProcessingJobRepository:

    @staticmethod
    async def create(
        session: AsyncSession,
        document_id: int,
        correlation_id: str,
    ) -> ProcessingJobDB:

        job = ProcessingJobDB(
            document_id=document_id,
            correlation_id=correlation_id,
            status="pending",
            attempt_count=0,
        )

        session.add(job)

        await session.flush()

        return job
