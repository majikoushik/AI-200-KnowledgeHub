def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

    assert data["database"] == "connected"


def test_version(client):

    response = client.get("/version")

    assert response.status_code == 200

    assert response.json()["version"] == "0.2.0"


def test_create_document(client):

    payload = {
        "title": "KEDA Overview",
        "category": "azure",
        "department": "cloud",
        "content": (
            "KEDA enables event-driven " "autoscaling of container " "workloads."
        ),
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


def test_create_and_get_document(client):

    payload = {
        "title": "Service Bus Overview",
        "category": "azure",
        "department": "integration",
        "content": ("Azure Service Bus provides " "durable enterprise messaging."),
    }

    create_response = client.post(
        "/documents",
        json=payload,
    )

    assert create_response.status_code == 201

    document_id = create_response.json()["document_id"]

    get_response = client.get(f"/documents/{document_id}")

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["document_id"] == document_id


def test_invalid_document(client):

    response = client.post(
        "/documents",
        json={
            "title": "",
            "category": "",
            "content": "abc",
        },
    )

    assert response.status_code == 422


def test_document_not_found(client):

    response = client.get("/documents/999999999")

    assert response.status_code == 404


def test_correlation_id(client):

    correlation_id = "test-correlation-id"

    response = client.get(
        "/health",
        headers={"X-Correlation-ID": correlation_id},
    )

    assert response.headers["X-Correlation-ID"] == correlation_id
