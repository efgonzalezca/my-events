from fastapi.testclient import TestClient


def test_health_response_carries_generated_request_id(client: TestClient) -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    rid = res.headers.get("x-request-id")
    assert rid and len(rid) >= 16


def test_incoming_request_id_is_echoed_back(client: TestClient) -> None:
    res = client.get("/api/health", headers={"x-request-id": "trace-abc-123"})
    assert res.status_code == 200
    assert res.headers["x-request-id"] == "trace-abc-123"
