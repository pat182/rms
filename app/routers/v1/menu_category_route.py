from app.core.dependencies import get_db
from ...dependencies import (
    get_authenticated_user
)
from fastapi import APIRouter, Depends



router = APIRouter(
    prefix="/v1/menus/{menu_id}/menu-categories",
    tags=["Menu Categories"],
    dependencies=[Depends(get_authenticated_user)],
)

