from ...model import DiningSession, CustomerOrder
from ...model.repositories import CustomerOrderRepo,CustomerOrderItemRepo
from ...schemas.customer_interface import CustomerCartRequest

from sqlalchemy.ext.asyncio import AsyncSession



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


    # async def get_order

