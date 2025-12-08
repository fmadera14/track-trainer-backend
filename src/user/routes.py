from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from src.user.models import User
from src.user.schema import UserRead

router = APIRouter()


@router.get("/", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
