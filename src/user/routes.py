from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from src.user.models import User
from src.user.schema import UserEdit
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
def edit_profile(
    user_edit: UserEdit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    username_exists = db.query(User).filter(User.username == user_edit.username).first()
    if username_exists:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    email_exists = db.query(User).filter(User.email == user_edit.email).first()
    if email_exists:
        raise HTTPException(status_code=400, detail="El correo ya existe")

    current_user.name = user_edit.name
    current_user.username = user_edit.username
    current_user.email = user_edit.email

    db.commit()
    db.refresh(current_user)

    return current_user
