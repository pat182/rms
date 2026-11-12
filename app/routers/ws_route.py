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
        manager.disconnect(group_id, websocket)


#==================Customer socket=======================

@router.websocket("/ws/join-request/{request_token}")
async def join_request_websocket(
    websocket: WebSocket,
    request_token: str,
):
    group_id = f"join_request:{request_token}"

    await manager.connect(group_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(group_id, websocket)

@router.websocket("/ws/dining-session/{session_token}")
async def dining_session_approval(
    websocket: WebSocket,
    session_token: str
):
    group_id = f"dining_session:{session_token}"
    await manager.connect(group_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:

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

        manager.disconnect(group_id, websocket)

@router.websocket("/ws/order_status/{session_token}")
async def order_status_update(
    websocket: WebSocket,
    session_token: str
):

    group_id = f"customer_session:{session_token}"
    await manager.connect(group_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(group_id, websocket)


#========================kitchen socket==============================
@router.websocket("/ws/kitchen-orders/{restaurant_id}")
async def kitchen_orders(
    websocket: WebSocket,
    restaurant_id: int,
    # current_user=Depends(get_authenticated_websocket_user),
):

    group_id = f"kitchen_orders:{restaurant_id}"

    await manager.connect(group_id, websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(group_id, websocket)