from app.core.security import SecurityInstance
from app.model.repositories import MenuRepository
from app.core.dependencies import get_db

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/test",
    tags=["Test"]
)

@router.get("/hash-password")
async def hash_password():
    hashed = SecurityInstance.hash_password("test123!@#")
    verify = SecurityInstance.verify_password("test123!@#", hashed)
    return {
        "success": True,
        "data":verify
    }

@router.get("/{test_id}/get-by-id")
async def get_by_id(test_id: int,db: AsyncSession = Depends(get_db)):
    menu = await MenuRepository(db).get_by_id(test_id)
    return {
        "success": True,
        "data": menu
    }