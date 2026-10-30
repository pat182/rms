
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.core.dependencies import get_db
from app.dependencies import get_authenticated_user
from app.dependencies.menu_dependencies.menu_dependecies import (
    get_menu_service,
    get_menu_item_service,
    get_menu_category_service,
)


class FakeTransaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeDB:
    def __init__(self):
        self.commit = AsyncMock()
        self.rollback = AsyncMock()

    def begin(self):
        return FakeTransaction()


@pytest.fixture
def db():
    return FakeDB()


@pytest.fixture
def auth_user():
    return SimpleNamespace(
        id=1,
        restaurants=[
            SimpleNamespace(id=1)
        ],
    )


@pytest.fixture
def menu_service():
    return AsyncMock()


@pytest.fixture
def item_service():
    return AsyncMock()


@pytest.fixture
def category_service():
    return AsyncMock()


@pytest.fixture
def client(
    db,
    auth_user,
    menu_service,
    item_service,
    category_service,
):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_authenticated_user] = lambda: auth_user

    app.dependency_overrides[get_menu_service] = lambda: menu_service
    app.dependency_overrides[get_menu_item_service] = lambda: item_service
    app.dependency_overrides[get_menu_category_service] = lambda: category_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
