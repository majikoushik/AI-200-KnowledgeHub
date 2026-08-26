import asyncio
import sys

import pytest

from dotenv import load_dotenv

# Load test environment BEFORE importing app.main
load_dotenv(".env.test", override=True)

import os

print("TEST DATABASE:", os.getenv("DATABASE_URL"))


# Windows fix for Psycopg async
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# IMPORTANT:
# Import the FastAPI application only AFTER
# configuring the Windows event-loop policy.

from fastapi.testclient import TestClient

from app.main import app

# ---------------------------------------------------------
# Test client
# ---------------------------------------------------------


@pytest.fixture(scope="session")
def client():

    with TestClient(app) as test_client:
        yield test_client
