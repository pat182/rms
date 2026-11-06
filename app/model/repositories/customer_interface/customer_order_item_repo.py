from app.core.base_repo import BaseRepo

from sqlalchemy import select
from app.model import CustomerOrderItem


class CustomerOrderItemRepo(BaseRepo):
    # SEARCH_FIELDS = ("session_token",)
    # SORT_FIELDS = ("started_at", "closed_at", "status")

    @property
    def model(self):
        return CustomerOrderItem