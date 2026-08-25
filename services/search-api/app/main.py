import logging
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status

from app.config import get_settings
from app.logging_config import configure_logging
from app.models import DocumentCreate, DocumentResponse
from app.store import (
    create_document_record,
    get_document_record,
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

    yield

    logger.info("application_stopping")


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


# ---------------------------------------------------------
# Request middleware
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
            "request_failed " "method=%s path=%s correlation_id=%s",
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
async def health():

    return {
        "status": "healthy",
        "service": "search-api",
        "environment": settings.environment,
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
# Create document
# ---------------------------------------------------------


@app.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    payload: DocumentCreate,
    request: Request,
):

    document = create_document_record(payload)

    logger.info(
        "document_received " "document_id=%s " "category=%s " "correlation_id=%s",
        document.document_id,
        document.category,
        request.state.correlation_id,
    )

    return document


# ---------------------------------------------------------
# Get document
# ---------------------------------------------------------


@app.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: int,
):

    document = get_document_record(document_id)

    if document is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document
