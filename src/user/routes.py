from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from src.auth.dependencies import get_current_user
from src.user.models import User
from src.user.schema import UserEdit

router = APIRouter()


@router.get("/")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at,
    }


@router.put("/")
def edit_profile(
    user_edit: UserEdit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    username_exists = db.query(User).filter(User.username == user_edit.username).first()
    if username_exists and username_exists.username != current_user.username:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    email_exists = db.query(User).filter(User.email == user_edit.email).first()
    if email_exists and email_exists.email != current_user.email:
        raise HTTPException(status_code=400, detail="El correo ya existe")

    current_user.name = user_edit.name
    current_user.username = user_edit.username
    current_user.email = user_edit.email

    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "username": current_user.username,
        "name": current_user.name,
        "email": current_user.email,
        "created_at": current_user.created_at,
    }
