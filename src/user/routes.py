from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from src.user.models import User
from src.user.schema import UserRead
from src.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "username": current_user.username,
        "created_at": current_user.created_at,
    }


@router.put("/")
async def edit_profile(current_user: User = Depends(get_current_user)):
    pass
