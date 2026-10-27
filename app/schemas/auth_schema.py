from app.schemas.user_schema import UserResponse
from app.core.base_schema import BaseSchema

from typing import Optional,Union


class LoginRequest(BaseSchema):
    email: str
    password: str

class Tokens(BaseSchema):
    expires_in: int
    expires_at: str
    r_expires_in: int
    r_expires_at: str
    user: UserResponse

class AppTokens(BaseSchema):
    access_token : str
    expires_in: int
    expires_at: str
    refresh_token: str
    r_expires_in: int
    r_expires_at: str

class TokenResponse(BaseSchema):
    csrf: Optional[str] = None
    token : Union[Tokens,AppTokens]
