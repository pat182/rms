import secrets,uuid
from typing import Optional
from datetime import datetime, timedelta, timezone

from app.core.security import SecurityInstance
from app.model.repositories import UserRepository
from app.model import UserRefreshToken, User, RestaurantUser, Restaurant
from app.helper import clear_auth_cookies

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

class AuthService:
    def __init__(self, db: AsyncSession, response: Response, device_info: str, client_type: str = 'browser'):
        self.db = db
        self.response = response
        self.client_type = client_type
        self.device_info = device_info

    async def access_tokens(self, email: str, password: str)->dict:
        user = await UserRepository(self.db).get_by_email(email)

        if not user or not SecurityInstance.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        csrf_token = secrets.token_urlsafe(32)
        access_token_expires = timedelta(minutes=SecurityInstance.jwt_min)
        access_token = SecurityInstance.create_token(
            data={
                "sub": str(user.id),
                "role_id": user.role_id,
                "client_type": self.client_type,
                "type": "access"
            },
            expires_delta=access_token_expires
        )
        expires_at = datetime.now(timezone.utc) + access_token_expires
        refresh_token_expires = timedelta(days=SecurityInstance.jwt_refresh_days)
        jti = str(uuid.uuid4())
        refresh_token = SecurityInstance.create_token(
            data={
                "sub": str(user.id),
                "type": "refresh",
                "client_type": self.client_type,
                "jti": jti,  # <-- added unique ID
                "iat": datetime.now(timezone.utc).timestamp()  # <-- added issued-at
            },
            expires_delta=refresh_token_expires
        )
        r_expires_at = datetime.now(timezone.utc) + refresh_token_expires
        db_ref_token = UserRefreshToken(
            user_id=user.id,
            jti=jti,
            refresh_token=refresh_token,
            device_info=self.device_info,
            expires_at=r_expires_at,
            revoked=False
        )

        self.db.add(db_ref_token)
        await self.db.commit()
        await self.db.refresh(db_ref_token)

        return {
            "access_token": access_token,
            "expires_in": int(access_token_expires.total_seconds()),
            "expires_at": f"{expires_at} UTC", "refresh_token": refresh_token,
            "r_expires_in": int(refresh_token_expires.total_seconds()),
            "r_expires_at": f"{r_expires_at} UTC",
            "csrf_token": csrf_token,
            "user": {
                "id" : user.id,
                "role_id" : user.role_id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "role": user.role,
                "restaurants" : [
                    ru.restaurants
                    for ru in user.restaurant_users
                    if ru.restaurants
                ]

            }
        }

    async def refresh_tokens(self, refresh_token: str,payload : dict):
        if not refresh_token:
            raise HTTPException(
                status_code=401,
                detail="Missing refresh token"
            )

        if payload.get("type") != "refresh":
            clear_auth_cookies(self.response)
            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )

        db_token: Optional[UserRefreshToken] = await self.db.scalar(
            select(UserRefreshToken).where(
                UserRefreshToken.user_id == int(payload["sub"]),
                UserRefreshToken.jti == payload["jti"],
                UserRefreshToken.revoked.is_(False)
            )
        )


        if not db_token or db_token.expires_at < datetime.now(timezone.utc):
            clear_auth_cookies(self.response)
            raise HTTPException(
                status_code=401,
                detail="Refresh token expired or revoked"
            )

        user = await self.db.scalar(
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.restaurant_users)
                .selectinload(RestaurantUser.restaurants)
                .selectinload(Restaurant.country)
            )
            .where(User.id == int(payload['sub']) )
        )

        if not user:
            clear_auth_cookies(self.response)
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        csrf_token = None if payload['client_type'] == 'app' else secrets.token_urlsafe(32)
        access_token_expires = timedelta(minutes=SecurityInstance.jwt_min)

        access_token = SecurityInstance.create_token(
            data={
                "sub": str(user.id),
                "role_id": user.role_id,
                "client_type": payload.get("client_type"),
                "type": "access"
            },
            expires_delta=access_token_expires
        )
        expires_at = datetime.now(timezone.utc) + access_token_expires
        refresh_token_expires = timedelta(days=SecurityInstance.jwt_refresh_days)
        new_jti = str(uuid.uuid4())

        new_refresh_token = SecurityInstance.create_token(
            data={
                "sub": str(user.id),
                "remember_me": True,
                "type": "refresh",
                "client_type": payload.get("client_type"),
                "jti": new_jti,
                "iat": datetime.now(timezone.utc).timestamp()
            },
            expires_delta=refresh_token_expires
        )
        refresh_expires_at = datetime.now(timezone.utc) + refresh_token_expires
        db_token.jti = new_jti
        db_token.refresh_token = new_refresh_token
        db_token.expires_at = refresh_expires_at

        await self.db.commit()

        return {
            "csrf_token": csrf_token,
            'access_token': access_token,
            "expires_in": int(access_token_expires.total_seconds()),
            "expires_at": f"{expires_at} UTC",
            'refresh_token': new_refresh_token,
            "r_expires_in": int((refresh_expires_at - datetime.now(timezone.utc)).total_seconds()),
            "r_expires_at": f"{refresh_expires_at} UTC",
            "user": {
                "id" : user.id,
                "role_id" : user.role_id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "role": user.role,
                "restaurants" : [
                    ru.restaurants
                    for ru in user.restaurant_users
                    if ru.restaurants
                ]

            }
        }

    async def me(self, payload:dict):

        user_id = int(payload["sub"])

        user = await UserRepository(
            self.db
        ).get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return user
