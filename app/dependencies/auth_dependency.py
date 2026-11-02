from ..core.security import SecurityInstance
from ..model.repositories import UserRepository
from ..core.dependencies import get_db

from fastapi import Request, HTTPException, Depends,WebSocket,WebSocketException,status
from sqlalchemy.ext.asyncio import AsyncSession

async def get_authenticated_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = SecurityInstance.token_validation(request)

    try:
        user_id = int(payload["sub"])

    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )

    user = await UserRepository(db).modified_get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user

async def get_authenticated_websocket_user(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    payload = SecurityInstance.websocket_token_validation(websocket)

    try:
        user_id = int(payload["sub"])

    except (KeyError, ValueError, TypeError):
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid authentication token",
        )

    user = await UserRepository(db).modified_get_by_id(user_id)

    if not user:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="User not found",
        )

    return user

def authorize_websocket_restaurant(
    auth_user,
    restaurant_id: int,
):
    restaurant_user = next(
        (
            ru
            for ru in auth_user.restaurant_users
            if ru.restaurant_id == restaurant_id
        ),
        None,
    )

    if not restaurant_user:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="You are not authorized to access this restaurant",
        )

    return restaurant_user.restaurants