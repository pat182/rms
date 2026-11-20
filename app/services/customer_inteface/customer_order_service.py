from fastapi.encoders import jsonable_encoder

from ...model import DiningSession, CustomerOrder
from ...model.repositories import CustomerOrderRepo,CustomerOrderItemRepo
from ...schemas.customer_interface import CustomerCartRequest, OrderStatusRequest

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


class CustomerOrderService:
    def __init__(self,db: AsyncSession):
        self.db = db
        self.repo = CustomerOrderRepo(self.db)
        self.model = self.repo.model

    @staticmethod
    def build_socket_order_payload(
            order: CustomerOrder,
            dining_session: DiningSession,
            event: str = "order_created",
    ):
        return jsonable_encoder({
            "event": event,
            "data": {
                "order": {
                    "id": order.id,
                    "table_number": dining_session.restaurant_table_id,
                    "status": order.status,
                    "created_at": order.created_at,
                    "items": [
                        {
                            "id": item.id,
                            "menu_item_id": item.menu_item_id,
                            "item_name": item.item_name,
                            "unit_price": item.unit_price,
                            "quantity": item.quantity,
                            "special_request": item.special_request,
                            "subtotal": item.subtotal,
                            "created_at": item.created_at,
                            "updated_at": item.updated_at,
                        }
                        for item in order.items
                    ],
                    "dining_session": dining_session,
                    "subtotal": order.subtotal,
                }
            }
        })

    @staticmethod
    def get_subtotal(items, price_key="unitPrice", quantity_key="quantity"):
        return sum(
            getattr(item, price_key) * getattr(item, quantity_key)
            for item in items
        )

    async def create_customer_order(
            self,
            payload: list[CustomerCartRequest],
            dining_sesh: DiningSession
    ) -> CustomerOrder:
        # from app.core.logger import log_info
        # log_info("=======================================")
        # log_info("PAYLOAD:", payload)
        # log_info("=======================================")
        order_subtotal = self.get_subtotal(payload)

        order = self.model(
            restaurant_id=dining_sesh.restaurant_table.restaurant_id,
            dining_session_token=dining_sesh.session_token,
            subtotal=order_subtotal,
        )

        order_item_repo = CustomerOrderItemRepo(self.db)

        order_items = []

        for item in payload:
            order_items.append(
                order_item_repo.model(
                    order=order,
                    menu_item_id=item.itemId,
                    item_name=item.itemName,
                    unit_price=item.unitPrice,
                    quantity=item.quantity,
                    special_request=item.specialRequest,
                    subtotal=item.unitPrice * item.quantity,
                )
            )

        self.db.add(order)

        await self.db.flush()

        return order

    async def update_customer_order_status(self,order_id:int,payload:OrderStatusRequest,session_token:str)->CustomerOrder:

        order = await self.repo.get_order_by_sesh(order_id,session_token)

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="order not found.",
            )

        order.status = payload.status
        order.cancel_reason = payload.cancel_reason

        return order

    async def cancel_order(self,order_id:int,session_token:str) -> CustomerOrder:

        order = await self.repo.get_order_by_sesh(order_id,session_token)

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Customer order not found.",
            )

        if order.status != "pending":
            raise HTTPException(
                status_code=400,
                detail="Customer order not found.",
            )

        order.status = "canceled"


        return order




