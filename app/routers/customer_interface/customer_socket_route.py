import json
from redis.asyncio import Redis

from ...core.websocket import manager
from ...dependencies import get_redis
from ...dependencies.customer_interface import customer_session_dependency
from ...model import DiningSession
from ...schemas.customer_interface import CustomerCartRequest

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/customer/socket",
    tags=["Customer Menu"]
)

@router.post("/{table_qr}/cart/{session_token}",)
async def save_items(
    # table_qr:str,
    session_token: str,
    payload: list[CustomerCartRequest],
    redis: Redis = Depends(get_redis),
    sesh_data : DiningSession = Depends(customer_session_dependency),
):
    # dining_sesh, is_new = sesh_data


    cart_data = [
        {
            **item.model_dump(mode="json"),
            "unitPrice": float(item.unitPrice)
        }
        for item in payload
    ]
    await redis.set(
        f"rms:cart:{session_token}",
        json.dumps(cart_data),
        ex=7200
    )

    await manager.broadcast(
        f"shared_cart:{session_token}",
        {
            "event": "cart_updated",
            "data": {
                "order" : [],
                "cart_items" : cart_data
            }
        }
    )

    return {
        "success" : True,
        "data" : session_token,
    }