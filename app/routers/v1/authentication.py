from pydantic import BaseModel

from ...dependencies import get_authenticated_user
from ...model import User
from ...services import AuthService
from ...core.dependencies import get_db
from ...core.security import SecurityInstance
from ...helper import set_auth_cookies,clear_auth_cookies
from ...schemas import LoginRequest, TokenResponse, Tokens, UserHttpResponse, UsersResponseV2

from fastapi import APIRouter, Depends,Request,Response,Cookie
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter(
    prefix="/v1/auth",
    tags=["Authentication"]
)

@router.post("",response_model=TokenResponse)
async def login(response: Response,request:Request, body: LoginRequest,db: AsyncSession = Depends(get_db)):
    auth = AuthService(db, response, request.state.device_info)

    token_data = await auth.access_tokens(email=body.email, password=body.password)

    set_auth_cookies(
        response, access_token=token_data['access_token'],
        refresh_token=token_data['refresh_token'],
        csrf_token=token_data['csrf_token'],
        access_exp=token_data['expires_in'],
        refresh_exp=token_data['r_expires_in'],
    )

    return TokenResponse(
        token=Tokens(**token_data),
        csrf=token_data['csrf_token'],
    )

@router.post("/refresh")
async def refresh( response: Response,request : Request,
             db: AsyncSession = Depends(get_db),
             refresh_token: str = Cookie(None) ):
    auth = AuthService(db, response, request.state.device_info)

    payload = SecurityInstance.token_validation(request, 'refresh')

    if payload.get('client_type') == 'browser':
        token_data = await auth.refresh_tokens(refresh_token, payload)
        # return token_data
        token_response = Tokens(**token_data)
        # from app.core.logger import log_info
        # log_info("==================================")
        # log_info("TOKEN", token_data)
        set_auth_cookies(
            response,
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            csrf_token=token_data['csrf_token'] if token_data['csrf_token'] else request.headers.get("X-CSRF-Token"),
            access_exp=token_data['expires_in'],
            refresh_exp=token_data['r_expires_in']
        )

    return TokenResponse(
        token=token_response,
        csrf=token_data['csrf_token'],
        user=token_data['user']
    )

@router.get("/me",response_model=UserHttpResponse)
async def me( auth_user: User = Depends(get_authenticated_user)):

    return UserHttpResponse(
        success=True,
        data=UsersResponseV2.model_validate(auth_user, from_attributes=True)
    )
