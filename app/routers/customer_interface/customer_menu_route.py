from ...dependencies.customer_interface import get_or_create_dining_session
from ...model import DiningSession
from ...core.websocket import manager


from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/customer/tables/{table_qr}",
    tags=["Customer Menu"]
)

@router.get("",)
async def get_menu(
    sesh_data : tuple[DiningSession,bool] = Depends(get_or_create_dining_session)
):
    dining_sesh, is_new = sesh_data
    restaurant = dining_sesh.restaurant_table.restaurant

    if is_new:
        await manager.broadcast(
                f"restaurant:{restaurant.id}",
                {
                    "event": "dining_session_created",
                    "data": {
                        "session_id": dining_sesh.id,
                        "session_token" : dining_sesh.session_token,
                        "table_name": dining_sesh.restaurant_table.table_name,
                        "status": dining_sesh.status,
                    },
                },
            )

    # from app.core.logger import log_info
    # log_info('=======================================')
    # log_info('DINING SESSION', restaurant)
    # log_info('=======================================')
    return {restaurant}
