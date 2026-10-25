from fastapi import FastAPI,Request

from app.core.config import settings
from app.routers.v1.restaurant import router as restaurant_router
from app.routers.v1.menu_route import router as menu_router
from app.routers.v1.menu_category_route import router as menu_category_router
from app.routers.v1.menu_item_route import router as menu_item_router
from app.routers.v1.authentication import router as authentication_router
from app.routers.test import router as test_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type","X-CSRF-Token","X-Client-Type"],
)

app.include_router(test_router)

app.include_router(authentication_router)
app.include_router(restaurant_router)
app.include_router(menu_router)
app.include_router(menu_category_router)
app.include_router(menu_item_router)


@app.middleware("http")
async def check_client_type(request: Request, call_next):
    auth_header = request.headers.get("Authorization", "").lower()

    if auth_header.startswith("bearer "):
        client_type = "app"
    else:
        client_type = "browser"

    request.state.client_type = client_type
    request.state.device_info = request.headers.get("User-Agent",f"Unknown-{client_type}")
    return await call_next(request)
