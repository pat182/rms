from pathlib import Path
from app.core.config import settings
from app.routers.v1 import (restaurant_router,menu_router,menu_category_router,menu_item_router,authentication_router)
from app.routers.test import router as test_router
from app.core.logger_config import setup_logging

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI,Request

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)
setup_logging()
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOADS_DIR),
    name="uploads",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS",],
    allow_headers=["Accept","Content-Type","X-CSRF-Token","X-Client-Type"],
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
