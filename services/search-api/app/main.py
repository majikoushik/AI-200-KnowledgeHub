import logging
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import (
    check_database_connection,
    close_database,
    get_db_session,
)
from app.logging_config import configure_logging
from app.models import (
    DocumentCreate,
    DocumentResponse,
)
from app.services.document_service import (
    DocumentService,
)

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

settings = get_settings()

configure_logging(settings.log_level)

logger = logging.getLogger("knowledgehub.search_api")


# ---------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        "application_starting " "name=%s version=%s environment=%s",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )

    try:

        await check_database_connection()

        logger.info("database_connection_successful")

    except Exception:

        # We deliberately don't crash the entire app here.
        # /health can report the dependency failure.
        logger.exception("database_connection_failed")

    yield

    await close_database()

    logger.info("application_stopping")


# ---------------------------------------------------------
# FastAPI
# ---------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------


@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):

    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid4()),
    )

    request.state.correlation_id = correlation_id

    start_time = perf_counter()

    try:

        response = await call_next(request)

    except Exception:

        logger.exception(
            "request_failed " "method=%s path=%s " "correlation_id=%s",
            request.method,
            request.url.path,
            correlation_id,
        )

        raise

    duration_ms = (perf_counter() - start_time) * 1000

    response.headers["X-Correlation-ID"] = correlation_id

    logger.info(
        "request_completed "
        "method=%s path=%s "
        "status_code=%s "
        "duration_ms=%.2f "
        "correlation_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        correlation_id,
    )

    return response


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------


@app.get("/health")
async def health(
    response: Response,
):

    try:

        await check_database_connection()

        return {
            "status": "healthy",
            "service": "search-api",
            "environment": settings.environment,
            "database": "connected",
        }

    except Exception:

        logger.exception("health_check_database_failed")

        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return {
            "status": "unhealthy",
            "service": "search-api",
            "environment": settings.environment,
            "database": "disconnected",
        }


# ---------------------------------------------------------
# Version
# ---------------------------------------------------------


@app.get("/version")
async def version():

    return {
        "name": settings.app_name,
        "version": settings.app_version,
    }


# ---------------------------------------------------------
# Create Document
# ---------------------------------------------------------


@app.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    payload: DocumentCreate,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):

    try:

        document = await DocumentService.create_document(
            session=session,
            payload=payload,
            correlation_id=(request.state.correlation_id),
        )

    except SQLAlchemyError as exc:

        logger.exception(
            "document_database_operation_failed " "correlation_id=%s",
            request.state.correlation_id,
        )

        raise HTTPException(
            status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
            detail="Database operation failed",
        ) from exc

    logger.info(
        "document_received " "document_id=%s " "category=%s " "correlation_id=%s",
        document.document_id,
        document.category,
        request.state.correlation_id,
    )

    return document


# ---------------------------------------------------------
# Get Document
# ---------------------------------------------------------


@app.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: int,
    session: AsyncSession = Depends(get_db_session),
):

    try:

        document = await DocumentService.get_document(
            session=session,
            document_id=document_id,
        )

    except SQLAlchemyError as exc:

        logger.exception(
            "document_lookup_failed " "document_id=%s",
            document_id,
        )

        raise HTTPException(
            status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
            detail="Database operation failed",
        ) from exc

    if document is None:

        raise HTTPException(
            status_code=(status.HTTP_404_NOT_FOUND),
            detail="Document not found",
        )

    return document
