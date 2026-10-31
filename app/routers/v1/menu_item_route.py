from ...core import dependencies
from ...core.dependencies import get_db
from ...dependencies import (get_menu_item_service,get_authenticated_user)
from ...model import User
from ...schemas import (CreateMenuItemRequest, CreateMenuItemResponse)
from ...schemas.menu.menu_item_schema import MenuItemResponse
from ...services.menu.menu_item_service import MenuItemService
from ...services import FileStorageService
from ...model.repositories import MenuItemRepository

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, File,Depends, UploadFile,HTTPException,Request

router = APIRouter(
    prefix="/v1/menus/{menu_id}/menu-items",
    tags=["Menu Items"],
    dependencies=[Depends(get_authenticated_user)]
)

@router.post("",response_model=CreateMenuItemResponse)
async def create_menu_item(
    menu_id: int,
    payload: list[CreateMenuItemRequest],
    db: AsyncSession = Depends(get_db),
    auth_user: User = Depends(get_authenticated_user),
    item_service: MenuItemService = Depends(get_menu_item_service)
):

    try:
        new_item = await item_service.create_menu_items(
            menu_id,
            payload,
            auth_user.restaurants[0].id
        )
        await db.commit()
        return CreateMenuItemResponse(
            success=True,
            data=new_item
        )
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create Menu Item",
        )
        raise



@router.post("/{menu_item_id}/menu-item-image")
async def upload_menu_item_image(
        menu_item_id: int,
        auth_user: User = Depends(get_authenticated_user),
        file: UploadFile = File(...),db: AsyncSession = Depends(get_db)
):
    file_storage_service = FileStorageService()
    menu_item_repo = MenuItemRepository(db)
    menu_item = await menu_item_repo.get_item(menu_item_id,auth_user.restaurants[0].id)

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
        # folder=f"{auth_user.restaurants[0].id}-{auth_user.restaurants[0].restaurant_name}-menu-items",
        folder=f"restaurant-{auth_user.restaurants[0].id}-menu-items"
    )
    try:
        menu_item.image_url = new_image_url
        await menu_item_repo.db.commit()

    except Exception:
        await menu_item_repo.db.rollback()

        try:
            await file_storage_service.delete_image(new_image_url)
        except Exception:
            #log
            pass

        raise HTTPException(
            status_code=500,
            detail="Failed to upload menu item image",
        )

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

@router.delete("/{menu_item_id}/menu-item-image",response_model=MenuItemResponse)
async def delete_menu_item_image(
    menu_item_id: int,
    request: Request,
    auth_user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
    item_service: MenuItemService = Depends(get_menu_item_service),

):
    try:
        body = await request.json()
        image_url = body.get("image_url")
        menu_item = await item_service.delete_item_image(menu_item_id,auth_user.restaurants[0].id,image_url)
        await db.commit()
        return MenuItemResponse(
            success=True,
            data=menu_item,
        )
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete menu item image",
        )


