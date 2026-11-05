from ...core.dependencies import get_db
from ...services.customer_inteface import CustomerOrderService

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_customer_order_service(db:AsyncSession=Depends(get_db))->CustomerOrderService:
    return CustomerOrderService(db)