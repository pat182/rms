import json
from redis.asyncio import Redis

from ...core.websocket import manager
from ...dependencies import get_redis

from fastapi import APIRouter, Depends,Request

from ...schemas.customer_interface import CustomerCartRequest

router = APIRouter(
    prefix="/customer/socket",
    tags=["Customer Menu"]
)

@router.post("/cart/{session_token}",)
async def save_items(
    session_token: str,
    payload: list[CustomerCartRequest],
    # redis: Redis = Depends(get_redis)
):
    cart_data = [
        {
            **item.model_dump(mode="json"),
            "unitPrice": float(item.unitPrice)
        }
        for item in payload
    ]
    # await redis.set(
    #     f"rms:cart:{session_token}",
    #     json.dumps(cart_data),
    #     ex=7200
    # )

    await manager.broadcast(
        f"shared_cart:{session_token}",
        {
            "event": "cart_updated",
            "data": cart_data
        }
    )


    return {
        "success" : True,
        "data" : session_token,
    }