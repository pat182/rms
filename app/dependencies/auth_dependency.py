from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import SecurityInstance
from ..model.repositories import UserRepository
from ..core.dependencies import get_db


async def get_authenticated_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = SecurityInstance.token_validation(request)

    try:
        user_id = int(payload["sub"])

    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )

    user = await UserRepository(db).modified_get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user