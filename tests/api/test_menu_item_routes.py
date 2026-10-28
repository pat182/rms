from unittest.mock import AsyncMock
from app.dependencies.menu_dependencies.menu_dependecies import get_menu_item_service

def test_create_menu_items_success(client):
    mock_service = AsyncMock()
    mock_service.create_menu_items.return_value = [
        {
            "id": 72,
            "menu_id": 1,
            "menu_category_id": None,
            "item_name": "Coke Large",
            "description": "440ml can",
            "price": "70.00",
            "image_url": None,
            "is_available": True,
            "sort_order": 1,
            "created_at": "2026-10-25T05:00:00Z",
            "updated_at": "2026-10-25T05:00:00Z",
        }
    ]

    async def override_get_menu_item_service():
        return mock_service

    client.app.dependency_overrides[get_menu_item_service] = (
        override_get_menu_item_service
    )

    try:
        response = client.post(
            "/v1/menus/1/menu-items/",
            json=[
                {
                    "menu_id": 1,
                    "menu_category_id": None,
                    "item_name": "Coke Large",
                    "description": "440ml can",
                    "price": 70,
                    "image_url": None,
                    "is_available": True,
                    "sort_order": 1,
                }
            ],
        )

        assert response.status_code == 200, response.text
        # print("RESPONSE:", response.json())
        # print("MOCK CALLED:", mock_service.create_menu_item.await_args_list)
        assert response.json()["success"] is True
        assert response.json()["data"][0]["item_name"] == "Coke Large"
        mock_service.create_menu_items.assert_awaited_once()
    finally:
        client.app.dependency_overrides.pop(get_menu_item_service, None)