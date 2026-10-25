from app.schemas.user_schema import UserResponse

from pydantic import BaseModel
from typing import Optional,Union


class LoginRequest(BaseModel):
    email: str
    password: str

class Tokens(BaseModel):
    expires_in: int
    expires_at: str
    r_expires_in: int
    r_expires_at: str
    user: UserResponse

class AppTokens(BaseModel):
    access_token : str
    expires_in: int
    expires_at: str
    refresh_token: str
    r_expires_in: int
    r_expires_at: str

class TokenResponse(BaseModel):
    csrf: Optional[str] = None
    token : Union[Tokens,AppTokens]
