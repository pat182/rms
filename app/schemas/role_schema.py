from datetime import datetime
from app.core.base_schema import BaseSchema
from pydantic import ConfigDict


class RoleData(BaseSchema):
    id: int
    role_name: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )