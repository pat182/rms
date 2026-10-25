from app.core.config import settings
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException,Request

class Security:
    def __init__(
            self,
            secret_key: str = settings.SECRET_KEY,
            algorithm: str = settings.JWT_HASHING_ALGORITHM,
            jwt_min: int = settings.JWT_MINUTES,
            jwt_refresh_days: int = settings.JWT_REFRESH_DAYS
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.jwt_min = jwt_min
        self.jwt_refresh_days = jwt_refresh_days

        self.password_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
        )


    def hash_password(self, password: str) -> str:

        safe_password = password.encode("utf-8")[:72]
        safe_password = safe_password.decode(
            "utf-8", errors="ignore"
        )
        return self.password_context.hash(safe_password)

    def verify_password(self,plain_password: str,hashed_password: str,) -> bool:
        safe_password = plain_password.encode("utf-8")[:72]
        safe_password = safe_password.decode(
            "utf-8", errors="ignore"
        )
        return self.password_context.verify(
            safe_password,
            hashed_password,
        )

    def create_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(tz=timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str):
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token expired"
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    def token_validation(self, request: Request, token_type: str = 'access') -> dict:
        cookie_token = request.cookies.get("access_token") if token_type == 'access' else request.cookies.get(
            "refresh_token")
        header_token = request.headers.get('Authorization')

        if cookie_token and header_token:
            raise HTTPException(
                status_code=401,
                detail="Both cookie and header present"
            )
        # web

        if cookie_token:

            if request.method != "GET":

                self.verify_csrf(
                    request.headers.get("X-CSRF-Token") if request.headers.get("X-CSRF-Token") else None,
                    request.cookies.get("csrf_token")
                )
            token = cookie_token

            payload = self.decode_token(token)
            if payload.get('client_type') != "browser":
                raise HTTPException(
                    status_code=401,
                    detail="Client Mismatched"
                )
        # app
        elif header_token:
            if not header_token.lower().startswith("bearer "):
                raise HTTPException(
                    status_code=401,
                    detail="Missing bearer token"
                )
            if request.headers.get("X-CSRF-Token") or request.cookies.get("csrf_token"):
                raise HTTPException(
                    status_code=401,
                    detail="CSRF not allowed in app flow"
                )
            token = header_token.split(" ", 1)[1]
            payload = self.decode_token(token)
            # print(payload)
            if payload.get('client_type') != "app":
                raise HTTPException(
                    status_code=401,
                    detail="Token Mismatched"
                )
        else:
            raise HTTPException(
                status_code=401,
                detail="Token Required"
            )

        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=401,
                detail="Token Type Mismatched"
            )
        return payload


    @staticmethod
    def verify_csrf(csrf_header: str | None, csrf_cookie: str | None):
        if not csrf_cookie or csrf_cookie != csrf_header:
            raise HTTPException(
                status_code=401,
                detail="CSRF validation failed"
            )


SecurityInstance = Security()