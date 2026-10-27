
from unittest.mock import AsyncMock

from fastapi import HTTPException


def test_create_menu_success(client, menu_service):
    menu_service.create_menu.return_value = {
        "id": 1,
        "restaurant_id": 1,
        "menu_name": "Test Menu",
        "description": None,
        "is_active": False,
        "created_at": "2026-10-25T05:00:00Z",
        "updated_at": "2026-10-25T05:00:00Z",
    }

    response = client.post(
        "/v1/menus/",
        json={
            "menu_name": "Test Menu",
            "description": None,
            "is_active": False,
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert body["data"]["menu_name"] == "Test Menu"
    menu_service.create_menu.assert_awaited_once()


def test_create_menu_validation_error(client, menu_service):
    response = client.post(
        "/v1/menus/",
        json={
            "description": "Missing menu name",
        },
    )

    assert response.status_code == 422
    menu_service.create_menu.assert_not_awaited()


def test_create_menu_service_error(client, menu_service):
    menu_service.create_menu.side_effect = RuntimeError("Database error")

    response = client.post(
        "/v1/menus/",
        json={"menu_name": "Test Menu"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to create menu"


def test_get_menu_success(client, menu_service):
    menu_service.get_menu.return_value = {
        "id": 1,
        "restaurant_id": 1,
        "menu_name": "Test Menu",
        "description": None,
        "is_active": False,
        "created_at": "2026-10-25T05:00:00Z",
        "updated_at": "2026-10-25T05:00:00Z",
        "categories": [],
        "menu_items": [],
    }

    response = client.get("/v1/menus/1")

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert body["data"]["id"] == 1
    assert body["data"]["categories"] == []
    assert body["data"]["menu_items"] == []

    menu_service.get_menu.assert_awaited_once_with(1)


def test_get_menu_not_found(client, menu_service):
    menu_service.get_menu.side_effect = HTTPException(
        status_code=404,
        detail="Menu not found",
    )

    response = client.get("/v1/menus/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Menu not found"

# def test_create_complete_menu_success(
#     client,
#     menu_service,
#     item_service,
#     category_service,
# ):
#     menu_service.create_complete_menu.return_value = {
#         "id": 26,
#         "restaurant_id": 1,
#         "menu_name": "Filipino Favorites",
#         "description": None,
#         "is_active": False,
#         "created_at": "2026-10-25T05:00:00Z",
#         "updated_at": "2026-10-25T05:00:00Z",
#         "menu_items": [
#             {
#                 "id": 72,
#                 "menu_id": 26,
#                 "menu_category_id": None,
#                 "item_name": "Coke Large",
#                 "description": "440ml can",
#                 "price": "70.00",
#                 "image_url": None,
#                 "is_available": True,
#                 "sort_order": 1,
#                 "created_at": "2026-10-25T05:00:00Z",
#                 "updated_at": "2026-10-25T05:00:00Z",
#             }
#         ],
#         "categories": [],
#     }
#
#     response = client.post(
#         "/v1/menus/complete",
#         json={
#             "menu_name": "Filipino Favorites",
#             "categories": [],
#             "menu_items": [
#                 {
#                     "menu_id": 1,
#                     "menu_category_id": None,
#                     "item_name": "Coke Large",
#                     "description": "440ml can",
#                     "price": 70,
#                     "image_url": None,
#                     "is_available": True,
#                     "sort_order": 1,
#                 }
#             ],
#         },
#     )
#
#     assert response.status_code == 200
#     body = response.json()
#
#     assert body["success"] is True
#     assert body["data"]["menu_name"] == "Filipino Favorites"
#     assert body["data"]["menu_items"][0]["item_name"] == "Coke Large"
#     assert body["data"]["categories"] == []
#
#     menu_service.create_complete_menu.assert_awaited_once_with(
#         # The route passes the validated request model, not the raw JSON.
#         menu_service.create_complete_menu.await_args.args[0],
#         item_service,
#         category_service,
#     )


def test_create_complete_menu_failure(
    client,
    menu_service,
):
    menu_service.create_complete_menu.side_effect = RuntimeError(
        "Insertion failed"
    )

    response = client.post(
        "/v1/menus/complete",
        json={"menu_name": "Broken Menu"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to create menu"
