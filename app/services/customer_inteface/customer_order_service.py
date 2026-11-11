

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
    def get_subtotal(items,key="unitPrice"):
        total = sum(getattr(item, key) for item in items)
        return total

    async def create_customer_order(
            self,
            payload: list[CustomerCartRequest],
            dining_sesh: DiningSession
    ) -> CustomerOrder:
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

    async def update_customer_order_status(self,order_id:int,payload:OrderStatusRequest,restaurant_id:int)->CustomerOrder:

        order = await self.repo.get_by_id(order_id,restaurant_id)

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="No active menu found for this restaurant.",
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

        await self.db.flush()
        return order




