from fastapi import HTTPException


def test_create_categories_success(client, category_service):
    category_service.create_menu_category.return_value = [
        {
            "id": 10,
            "menu_id": 1,
            "parent_id": None,
            "category_name": "Main Courses",
            "sort_order": 0,
            "created_at": "2026-10-25T05:00:00Z",
            "updated_at": "2026-10-25T05:00:00Z",
            "subcategories": [],
        }
    ]

    response = client.post(
        "/v1/menus/1/menu-categories/",
        json=[
            {
                "category_name": "Main Courses",
                "sort_order": 0,
                "subcategories": [],
            }
        ],
    )

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert body["data"][0]["category_name"] == "Main Courses"

    category_service.create_menu_category.assert_awaited_once()


def test_create_categories_menu_not_found(client, category_service):
    category_service.create_menu_category.side_effect = HTTPException(
        status_code=404,
        detail="Menu not found",
    )

    response = client.post(
        "/v1/menus/999/menu-categories/",
        json=[{"category_name": "Main Courses"}],
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Menu not found"