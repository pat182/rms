from typing import Generic, TypeVar, List
from app.core.base_schema import BaseSchema

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class PaginatedResponse(BaseSchema, Generic[T]):
    page: int
    page_size: int
    total_items: int
    data: List[T]

    model_config = ConfigDict(from_attributes=True)