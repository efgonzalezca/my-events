from fastapi.testclient import TestClient


def _register(
    client: TestClient,
    email: str = "example@test.com",
    password: str = "S1$#a1pa$$w0rd",
    full_name: str = "Alice",
):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )


def _login(
    client: TestClient,
    email: str = "example@test.com",
    password: str = "S1$#a1pa$$w0rd",
):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


def test_register_success(client: TestClient) -> None:
    res = _register(client)
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "example@test.com"
    assert body["full_name"] == "Alice"
    assert body["role"] == "attendee"
    assert body["is_active"] is True
    assert isinstance(body["id"], int)


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    _register(client)
    res = _register(client)
    assert res.status_code == 409
    assert res.json()["code"] == "EMAIL_ALREADY_EXISTS"


def test_login_success_returns_bearer_token(client: TestClient) -> None:
    _register(client)
    res = _login(client)
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]


def test_login_invalid_password_returns_401(client: TestClient) -> None:
    _register(client)
    res = _login(client, password="wrongpass1234")
    assert res.status_code == 401
    assert res.json()["code"] == "INVALID_CREDENTIALS"


def test_me_with_valid_token_returns_user(client: TestClient) -> None:
    _register(client)
    token = _login(client).json()["access_token"]
    res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == "example@test.com"
    assert body["role"] == "attendee"


def test_me_without_token_is_rejected(client: TestClient) -> None:
    res = client.get("/api/auth/me")
    assert res.status_code in (401, 403)