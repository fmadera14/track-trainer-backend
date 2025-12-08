from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from src.auth.dependencies import get_current_user
from src.exercise.models import Exercise
from src.exercise.schemas import ExerciseCreate
from src.user.models import User

router = APIRouter()


@router.get("/")
async def list_exercises(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    exercises = db.query(Exercise).filter(Exercise.user_id == current_user.id).all()
    return exercises


@router.post("/")
async def create_exercise(
    exercise_data: ExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise_exist = (
        db.query(Exercise).filter(Exercise.name == exercise_data.name).first()
    )

    if exercise_exist:
        raise HTTPException(
            status_code=400, detail="El nombre del ejercicio ya está en uso"
        )

    new_exercise = Exercise(
        user_id=current_user.id,
        name=exercise_data.name,
        description=exercise_data.description,
        muscle_group=exercise_data.muscle_group,
    )

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    return new_exercise
