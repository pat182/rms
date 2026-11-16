
from fastapi import APIRouter

router = APIRouter(
    prefix = "/v1/dashboard",
    tags=["Dashboard"],
)

@router.get("")
async def index(

):
    pass