from typing import Generic, TypeVar, List

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    page: int
    page_size: int
    total_items: int
    data: List[T]

    model_config = ConfigDict(from_attributes=True)