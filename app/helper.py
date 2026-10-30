from fastapi import Response

def clear_auth_cookies(response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    response.delete_cookie(key="csrf_token", path="/")

def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    csrf_token: str,
    access_exp: int,
    refresh_exp: int
):
    # Access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        # samesite="lax",
        samesite="none",
        secure=True,   # always True in production
        max_age=access_exp,
        path="/"
    )

    # Refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        # samesite="lax",
        samesite="none",
        secure=True,
        max_age=refresh_exp,
        path="/"
    )
    if csrf_token:
    # CSRF token cookie (not HttpOnly)
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,
            # samesite="lax",
            samesite="none",
            secure=True,
            max_age=refresh_exp,
            path="/"
        )