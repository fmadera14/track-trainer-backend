from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from src.auth.dependencies import get_current_user
from src.exercise.models import Exercise
from src.user.models import User

router = APIRouter()


@router.get("/")
async def list_exercises(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    exercises: list[Exercise] = db.query(Exercise).filter(
        Exercise.user_id == current_user.id
    )
    return exercises
