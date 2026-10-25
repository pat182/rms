from app.core.dependencies import get_db
from app.schemas import (CreateMenuItemRequest)
from app.services.menu.menu_item_service import MenuItemService
from app.services import FileStorageService
from app.model.repositories import MenuItemRepository


from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, File,Depends, UploadFile,HTTPException

router = APIRouter(
    prefix="/v1/menus/{menu_id}/menu-items",
    tags=["Menu Items"]
)

@router.post("/",)
async def create_menu_item(menu_id:int,payload: list[CreateMenuItemRequest], db: AsyncSession = Depends(get_db) ):
    menu_item_service = MenuItemService(db=db)

    new_item = await menu_item_service.create_menu_item(menu_id, payload)

    return {
        "success": True,
        "data" : new_item
    }


@router.post("/{menu_item_id}/menu-item-image")
async def upload_menu_item_image(menu_item_id: int,file: UploadFile = File(...),db: AsyncSession = Depends(get_db)):
    file_storage_service = FileStorageService()
    menu_item_repo = MenuItemRepository(db)
    menu_item = await menu_item_repo.get_by_id(menu_item_id)

    if menu_item is None:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found.",
        )
    # Preserve the old image URL.
    old_image_url = menu_item.image_url
    # Save the new image first.
    new_image_url = await file_storage_service.save_image(
        file=file,
        folder="1-creepy-restaurant-menu-items",
    )

    try:
        menu_item.image_url = new_image_url
        await menu_item_repo.db.commit()

    except Exception:
        await menu_item_repo.db.rollback()

        try:
            await file_storage_service.delete_image(new_image_url)
        except Exception:
            # Log cleanup failure in production.
            pass

        raise

    if old_image_url and old_image_url != new_image_url:
        try:
            await file_storage_service.delete_image(old_image_url)
        except Exception:
            # Log this failure
            pass

    return {
        "success": True,
        "data": {
            "image_url": new_image_url,
        },
    }
