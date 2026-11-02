from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends

from app.core.websocket import manager
from app.dependencies import (get_authenticated_websocket_user,authorize_websocket_restaurant)

router = APIRouter()


@router.websocket("/ws/customer_status/{restaurant_id}")
async def customer_status_notification(
        websocket: WebSocket,
        restaurant_id: int,
        current_user=Depends(get_authenticated_websocket_user),
):
    authorize_websocket_restaurant(current_user, restaurant_id)
    group_id = f"restaurant:{restaurant_id}"

    from app.core.logger import log_info
    log_info('=======================================')
    log_info('ORIGIN', websocket.headers.get("origin"))
    log_info('COOKIE', websocket.headers.get("cookie"))
    log_info('=======================================')
    await manager.connect(group_id, websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(group_id, websocket)