from unittest.mock import AsyncMock

from fastapi import HTTPException

from app.routers.v1 import restaurant as restaurant_route


def restaurant_data():
    return {
        "id": 5,
        "country_id": 1,
        "restaurant_name": "Dummy Restaurant",
        "contact_number": "09123456789",
        "address": "123 Test Street",
        "email": "dummy@example.com",
        "is_active": True,
        "country": {
            "id": 1,
            "country_name": "Test Country",
            "country_code": "TC",
            "phone_code": "+1",
        },
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }


def test_list_restaurants_success(client, monkeypatch):
    restaurants = [restaurant_data()]
    repository = AsyncMock()
    repository.filter.return_value = (restaurants, 1)
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantRepository",
        lambda db: repository,
    )

    response = client.get(
        "/v1/restaurants?page=2&page_size=5&sort_by=restaurant_name"
        "&sort_order=asc&search=Dummy"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert body["page_size"] == 5
    assert body["total_items"] == 1
    assert body["data"][0]["restaurant_name"] == "Dummy Restaurant"
    repository.filter.assert_awaited_once()
    args, kwargs = repository.filter.await_args
    assert args == (2, 5, "restaurant_name", "asc", "Dummy")
    assert kwargs["relationships"] == [restaurant_route.Restaurant.country]


def test_list_restaurants_rejects_invalid_pagination(client, monkeypatch):
    repository = AsyncMock()
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantRepository",
        lambda db: repository,
    )

    response = client.get("/v1/restaurants?page=0")

    assert response.status_code == 422
    repository.filter.assert_not_awaited()


def test_get_restaurant_success(client, monkeypatch, auth_user):
    service = AsyncMock()
    service.get_restaurant.return_value = restaurant_data()
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantService",
        lambda db: service,
    )

    response = client.get("/v1/restaurants/5")

    assert response.status_code == 200
    assert response.json()["data"]["restaurant_name"] == "Dummy Restaurant"
    service.get_restaurant.assert_awaited_once_with(5, auth_user)


def test_get_restaurant_http_error_is_preserved(client, monkeypatch):
    service = AsyncMock()
    service.get_restaurant.side_effect = HTTPException(
        status_code=404,
        detail="Restaurant not found",
    )
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantService",
        lambda db: service,
    )

    response = client.get("/v1/restaurants/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"


def test_get_restaurant_unexpected_error(client, monkeypatch):
    service = AsyncMock()
    service.get_restaurant.side_effect = RuntimeError("failed")
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantService",
        lambda db: service,
    )

    response = client.get("/v1/restaurants/5")

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to get restaurant"


def test_update_restaurant_status_success(
    client,
    monkeypatch,
    auth_user,
    db,
):
    service = AsyncMock()
    updated = restaurant_data()
    updated["is_active"] = False
    service.update_status.return_value = updated
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantService",
        lambda session: service,
    )

    response = client.put(
        "/v1/restaurants/5/status",
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["data"]["is_active"] is False
    service.update_status.assert_awaited_once_with(5, False, auth_user)
    db.commit.assert_awaited_once()
    db.rollback.assert_not_awaited()


def test_update_restaurant_status_http_error_rolls_back(
    client,
    monkeypatch,
    db,
):
    service = AsyncMock()
    service.update_status.side_effect = HTTPException(
        status_code=404,
        detail="Restaurant not found",
    )
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantService",
        lambda session: service,
    )

    response = client.put(
        "/v1/restaurants/5/status",
        json={"is_active": False},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurant not found"
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once()


def test_update_restaurant_status_unexpected_error_rolls_back(
    client,
    monkeypatch,
    db,
):
    service = AsyncMock()
    service.update_status.side_effect = RuntimeError("failed")
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantService",
        lambda session: service,
    )

    response = client.put(
        "/v1/restaurants/5/status",
        json={"is_active": False},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to update status"
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once()


def test_create_restaurant_success(client, monkeypatch, auth_user, db):
    service = AsyncMock()
    service.create_restaurant.return_value = restaurant_data()
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantService",
        lambda session: service,
    )

    response = client.post(
        "/v1/restaurants",
        json={
            "country_id": 1,
            "restaurant_name": "Dummy Restaurant",
            "contact_number": "09123456789",
            "address": "123 Test Street",
            "email": "dummy@example.com",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["restaurant_name"] == "Dummy Restaurant"
    payload, received_user = service.create_restaurant.await_args.args
    assert payload.restaurant_name == "Dummy Restaurant"
    assert received_user is auth_user
    db.commit.assert_awaited_once()
    db.rollback.assert_not_awaited()


def test_create_restaurant_http_error_rolls_back(
    client,
    monkeypatch,
    db,
):
    service = AsyncMock()
    service.create_restaurant.side_effect = HTTPException(
        status_code=400,
        detail="Restaurant already exists",
    )
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantService",
        lambda session: service,
    )

    response = client.post(
        "/v1/restaurants",
        json={
            "country_id": 1,
            "restaurant_name": "Dummy Restaurant",
            "contact_number": "09123456789",
            "address": "123 Test Street",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Restaurant already exists"
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once()


def test_create_restaurant_unexpected_error_rolls_back(
    client,
    monkeypatch,
    db,
):
    service = AsyncMock()
    service.create_restaurant.side_effect = RuntimeError("failed")
    monkeypatch.setattr(
        restaurant_route,
        "RestaurantService",
        lambda session: service,
    )

    response = client.post(
        "/v1/restaurants",
        json={
            "country_id": 1,
            "restaurant_name": "Dummy Restaurant",
            "contact_number": "09123456789",
            "address": "123 Test Street",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to create restaurant"
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once()
