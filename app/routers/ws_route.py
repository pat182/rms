from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends

from app.core.websocket import manager
from app.dependencies import (get_authenticated_websocket_user,authorize_websocket_restaurant)

router = APIRouter()


@router.websocket("/ws/admin_notification/{restaurant_id}")
async def admin_notification(
        websocket: WebSocket,
        restaurant_id: int,
        current_user=Depends(get_authenticated_websocket_user),
):
    authorize_websocket_restaurant(current_user, restaurant_id)
    group_id = f"restaurant:{restaurant_id}"

    await manager.connect(group_id, websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        # from app.core.logger import log_info
        # log_info('=======================================')
        # log_info('sadasdasd')
        # log_info('=======================================')
        manager.disconnect(group_id, websocket)

@router.websocket("/ws/shared-cart/{session_token}")
async def shared_cart(
    websocket: WebSocket,
    session_token: str
):
    group_id = f"shared_cart:{session_token}"
    await manager.connect(group_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        # from app.core.logger import log_info
        # log_info('=======================================')
        # log_info('sadasdasd')
        # log_info('=======================================')
        manager.disconnect(group_id, websocket)