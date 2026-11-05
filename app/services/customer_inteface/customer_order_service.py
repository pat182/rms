
from sqlalchemy.ext.asyncio import AsyncSession


class CustomerOrderService:
    def __init__(self,db: AsyncSession):
        self.db = db

