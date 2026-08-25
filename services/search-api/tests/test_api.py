from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "search-api"


def test_version():

    response = client.get("/version")

    assert response.status_code == 200

    data = response.json()

    assert data["version"] == "0.1.0"


def test_create_document():

    payload = {
        "title": "KEDA Overview",
        "category": "azure",
        "department": "cloud",
        "content": ("KEDA enables event-driven " "autoscaling of workloads."),
    }

    response = client.post(
        "/documents",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["document_id"] > 0
    assert data["title"] == "KEDA Overview"
    assert data["status"] == "received"


def test_get_document():

    payload = {
        "title": "Container Apps",
        "category": "azure",
        "department": "cloud",
        "content": ("Azure Container Apps provides " "managed container hosting."),
    }

    create_response = client.post(
        "/documents",
        json=payload,
    )

    document_id = create_response.json()["document_id"]

    get_response = client.get(f"/documents/{document_id}")

    assert get_response.status_code == 200

    assert get_response.json()["document_id"] == document_id


def test_invalid_document():

    payload = {
        "title": "",
        "category": "",
        "content": "abc",
    }

    response = client.post(
        "/documents",
        json=payload,
    )

    assert response.status_code == 422


def test_document_not_found():

    response = client.get("/documents/999999")

    assert response.status_code == 404
