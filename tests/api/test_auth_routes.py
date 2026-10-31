from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException


def test_login_success(client):
    # ///browser
    now = datetime.now(timezone.utc).isoformat()

    token_data = {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "expires_in": 900,
        "expires_at": now,
        "r_expires_in": 604800,
        "r_expires_at": now,
        "csrf_token": "test-csrf-token",
        "user": {
            "id": 1,
            "role_id": 1,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "created_at": now,
            "updated_at": now,
            "role": {
                "id": 1,
                "role_name": "Admin",
                "created_at": now,
                "updated_at": now,
            },
            "restaurants": [
                {
                    "id": 1,
                    "country_id": 1,
                    "restaurant_name": "Test Restaurant",
                    "contact_number": "09123456789",
                    "address": "Test Address",
                    "email": "restaurant@example.com",
                    "is_active": True,
                    "country": {
                        "id": 1,
                        "country_name": "philippines",
                        "country_code": "ph",
                        "phone_code": "+63"
                    },
                    "created_at": now,
                    "updated_at": now,
                }
            ],
        },
    }

    with patch("app.routers.v1.authentication.AuthService") as mock_auth:
        mock_auth.return_value.access_tokens = AsyncMock(
            return_value=token_data
        )

        response = client.post(
            "/v1/auth/",
            json={
                "email": "test@example.com",
                "password": "test-password",
            },
        )

    assert response.status_code == 200
    assert response.json()["csrf"] == "test-csrf-token"

    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    assert "csrf_token" in response.cookies

    mock_auth.return_value.access_tokens.assert_awaited_once_with(
        email="test@example.com",
        password="test-password",
    )

def test_login_invalid_credentials(client):
    with patch("app.routers.v1.authentication.AuthService") as mock_auth:
        mock_auth.return_value.access_tokens = AsyncMock(
            side_effect=HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )
        )

        response = client.post(
            "/v1/auth/",
            json={
                "email": "wrong@example.com",
                "password": "wrong-password",
            },
        )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid credentials"
    }

    mock_auth.return_value.access_tokens.assert_awaited_once_with(
        email="wrong@example.com",
        password="wrong-password",
    )

def test_me_success(client, auth_user):
    response = client.get("/v1/auth/me")

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["id"] == auth_user.id

def test_me_unauthenticated(auth_client):
    response = auth_client.get("/v1/auth/me")

    assert response.status_code == 401