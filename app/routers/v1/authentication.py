from pydantic import BaseModel

from ...dependencies import get_authenticated_user
from ...model import User, UserRefreshToken
from ...model.repositories import UserRefreshTokenRepository
from ...services import AuthService
from ...core.dependencies import get_db
from ...core.security import SecurityInstance
from ...helper import set_auth_cookies,clear_auth_cookies
from ...schemas import LoginRequest, TokenResponse, Tokens, UserHttpResponse, UsersResponseV2, AppTokens

from fastapi import APIRouter, Depends, Request, Response, Cookie, Header
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter(
    prefix="/v1/auth",
    tags=["Authentication"]
)

@router.post("/app")
async def app_login(
    response: Response,
    request:Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    auth = AuthService(db, response, request.state.device_info,"app")

    token_data = await auth.access_tokens(email=body.email, password=body.password)

    return TokenResponse(
        token=AppTokens(**token_data),
        user=token_data['user']
    )


@router.post("",response_model=TokenResponse)
async def login(
        response: Response,
        request:Request,
        body: LoginRequest,
        db: AsyncSession = Depends(get_db)
):

    auth = AuthService(db, response, request.state.device_info)

    token_data = await auth.access_tokens(email=body.email, password=body.password)

    set_auth_cookies(
        response,
        access_token=token_data['access_token'],
        refresh_token=token_data['refresh_token'],
        csrf_token=token_data['csrf_token'],
        access_exp=token_data['expires_in'],
        refresh_exp=token_data['r_expires_in'],
    )
    return TokenResponse(
        token=Tokens(**token_data),
        csrf=token_data['csrf_token'],
    )

@router.post("/refresh",response_model=TokenResponse)
async def refresh(
    response: Response,request : Request,
    db: AsyncSession = Depends(get_db),
    refresh_token: str = Cookie(None),
    authorization: str | None = Header(default=None),
):

    auth = AuthService(db, response, request.state.device_info,request.state.client_type)

    payload = SecurityInstance.token_validation(request, 'refresh')

    if payload.get('client_type') == 'browser':

        token_data = await auth.refresh_tokens(refresh_token, payload)

        token_response = Tokens(**token_data)

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

    else:

        refresh_token = authorization.split(" ", 1)[1]
        token_data = await auth.refresh_tokens(refresh_token, payload)
        token_response = Tokens(**token_data)

        return TokenResponse(
            token=AppTokens(**token_data),
            user=token_response.user
        )



@router.get("/me",response_model=UserHttpResponse)
async def me( auth_user: User = Depends(get_authenticated_user)):

    return UserHttpResponse(
        success=True,
        data=UsersResponseV2.model_validate(auth_user, from_attributes=True)
    )

@router.post("/logout")
async def logout(
        response: Response,
        request: Request,
        db: AsyncSession = Depends(get_db)

):
    refresh_token = request.cookies.get("refresh_token")
    ref_repo = UserRefreshTokenRepository(db)

    if refresh_token:
        result = await ref_repo.get_by_refresh_token(refresh_token)
        token = result.scalar_one()
        if token:
            token.revoked = True
            await db.commit()

    clear_auth_cookies(response)

    return {
        "success": True,
        "message": "Logged out successfully",
    }