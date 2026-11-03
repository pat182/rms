from unittest.mock import AsyncMock

from fastapi import HTTPException
import pytest

from app.dependencies.restaurant_dependencies import get_restaurant_table_service


@pytest.fixture
def table_service():
    return AsyncMock()


@pytest.fixture
def table_client(client, monkeypatch, table_service):
    monkeypatch.setitem(
        client.app.dependency_overrides,
        get_restaurant_table_service,
        lambda: table_service,
    )
    return client


def test_create_restaurant_tables_success(table_client, table_service, db):
    table_service.create_resto_table.return_value = [
        {
            "id": 7,
            "restaurant_id": 1,
            "table_name": "Patio 1",
            "capacity": 4,
            "is_active": True,
            "qr_token": "dummy-qr-token",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        }
    ]

    response = table_client.post(
        "/v1/restaurant-table",
        json=[{"table_name": "Patio 1", "capacity": 4}],
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": [
            {
                "id": 7,
                "restaurant_id": 1,
                "table_name": "Patio 1",
                "capacity": 4,
                "is_active": True,
                "qr_token": "dummy-qr-token",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
            }
        ],
    }

    restaurant, payload = table_service.create_resto_table.await_args.args
    assert restaurant.id == 1
    assert len(payload) == 1
    assert payload[0].table_name == "Patio 1"
    assert payload[0].capacity == 4
    db.commit.assert_awaited_once()
    db.rollback.assert_not_awaited()


def test_create_restaurant_tables_failure(table_client, table_service, db):
    table_service.create_resto_table.side_effect = RuntimeError("failed")

    response = table_client.post(
        "/v1/restaurant-table",
        json=[{"table_name": "Patio 1", "capacity": 4}],
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to create table"
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once()


def test_update_dining_session_status_success(
    table_client,
    table_service,
    db,
):
    table_service.update_table_sesh_status.return_value = {
        "id": 3,
        "status": "verified",
    }

    response = table_client.patch(
        "/v1/dining-session/dummy-session-token/status",
        json={"status": "verified"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"id": 3, "status": "verified"},
    }
    session_token, payload = (
        table_service.update_table_sesh_status.await_args.args
    )
    assert session_token == "dummy-session-token"
    assert payload.status == "verified"
    db.commit.assert_awaited_once()
    db.rollback.assert_not_awaited()


def test_update_dining_session_status_http_error(
    table_client,
    table_service,
    db,
):
    table_service.update_table_sesh_status.side_effect = HTTPException(
        status_code=404,
        detail="Dining session not found",
    )

    response = table_client.patch(
        "/v1/dining-session/dummy-session-token/status",
        json={"status": "rejected"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Dining session not found"
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once()


def test_update_dining_session_status_unexpected_error(
    table_client,
    table_service,
    db,
):
    table_service.update_table_sesh_status.side_effect = RuntimeError("failed")

    response = table_client.patch(
        "/v1/dining-session/dummy-session-token/status",
        json={"status": "pending"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Failed to update dining session status"
    )
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once()


def test_update_dining_session_status_rejects_invalid_status(
    table_client,
    table_service,
):
    response = table_client.patch(
        "/v1/dining-session/dummy-session-token/status",
        json={"status": "finished"},
    )

    assert response.status_code == 422
    table_service.update_table_sesh_status.assert_not_awaited()


def test_update_restaurant_table_success(table_client, table_service, db):
    table_service.update_resto_table.return_value = {
        "id": 7,
        "restaurant_id": 1,
        "table_name": "Patio 1",
        "capacity": 4,
        "is_active": True,
        "qr_token": "dummy-qr-token",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }

    response = table_client.patch(
        "/v1/restaurant-table/7",
        json={"table_name": "Patio 1", "capacity": 4},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "id": 7,
            "restaurant_id": 1,
            "table_name": "Patio 1",
            "capacity": 4,
            "is_active": True,
            "qr_token": "dummy-qr-token",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        },
    }

    table_id, payload, restaurant_id = (
        table_service.update_resto_table.await_args.args
    )
    assert table_id == 7
    assert payload.table_name == "Patio 1"
    assert payload.capacity == 4
    assert payload.is_active is True
    assert restaurant_id == 1
    db.commit.assert_awaited_once()
    db.rollback.assert_not_awaited()


def test_update_restaurant_table_failure(table_client, table_service, db):
    table_service.update_resto_table.side_effect = RuntimeError("failed")

    response = table_client.patch(
        "/v1/restaurant-table/7",
        json={"table_name": "Patio 1", "capacity": 4},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to update restaurant table"
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once()
