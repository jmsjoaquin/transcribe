from datetime import UTC, datetime

from app.models.user import User


def test_register_returns_created_user(client, fake_db, monkeypatch) -> None:
    def fake_register_user(db, payload):
        assert db is fake_db
        assert payload.email == "ali@example.com"
        return User(
            id=10,
            email=payload.email,
            hashed_password="hashed",
            given_name=payload.given_name,
            last_name=payload.last_name,
            is_active=True,
            created_at=datetime(2026, 3, 27, tzinfo=UTC),
        )

    monkeypatch.setattr("app.api.routes.auth.register_user", fake_register_user)

    response = client.post(
        "/auth/register",
        json={
            "email": "ali@example.com",
            "given_name": "Ali",
            "last_name": "Test",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "ali@example.com"


def test_login_sets_cookie(client, fake_db, monkeypatch) -> None:
    def fake_authenticate_user(db, payload):
        assert db is fake_db
        return (
            User(
                id=1,
                email=payload.email,
                hashed_password="hashed",
                given_name="Ali",
                last_name="Test",
                is_active=True,
                created_at=datetime(2026, 3, 27, tzinfo=UTC),
            ),
            "token-123",
        )

    monkeypatch.setattr("app.api.routes.auth.authenticate_user", fake_authenticate_user)

    response = client.post(
        "/auth/login",
        json={"email": "ali@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful."
    assert "access_token=token-123" in response.headers["set-cookie"]


def test_logout_clears_cookie(client) -> None:
    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logout successful."}
    assert "access_token=\"\"" in response.headers["set-cookie"]
