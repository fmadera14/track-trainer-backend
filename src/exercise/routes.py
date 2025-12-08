from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from src.auth.dependencies import get_current_user
from src.exercise.models import Exercise
from src.exercise.schemas import ExerciseCreate
from src.user.models import User

router = APIRouter()


@router.get("/")
async def list_exercises(
    name: str | None = None,
    muscle_group: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Exercise).filter(Exercise.user_id == current_user.id)

    if name:
        query = query.filter(Exercise.name.ilike(f"%{name}%"))

    if muscle_group:
        query = query.filter(Exercise.muscle_group.ilike(f"%{muscle_group}%"))

    exercises = query.all()
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


@router.put("/{exercise_id}")
async def edit_exercise(
    exercise_id: int,
    exercise_data: ExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise_exists = (
        db.query(Exercise)
        .filter(
            Exercise.name == exercise_data.name, Exercise.user_id == current_user.id
        )
        .first()
    )

    if exercise_exists and exercise_data.name != exercise_exists.name:
        raise HTTPException(
            status_code=400, detail="El nombre del ejercicio ya está en uso"
        )

    exercise = (
        db.query(Exercise)
        .filter(Exercise.id == exercise_id, Exercise.user_id == current_user.id)
        .first()
    )

    if not exercise:
        raise HTTPException(status_code=404, detail="No se encontró el ejercicio")

    exercise.name = exercise_data.name
    exercise.muscle_group = exercise_data.muscle_group
    exercise.description = exercise_data.description

    db.commit()
    db.refresh(exercise)

    return {
        "id": exercise.id,
        "name": exercise.name,
        "description": exercise.description,
        "muscle_group": exercise.muscle_group,
        "created_at": exercise.created_at,
    }


@router.delete("/{exercise_id}")
async def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise = (
        db.query(Exercise)
        .filter(Exercise.id == exercise_id, Exercise.user_id == current_user.id)
        .first()
    )

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )

    db.delete(exercise)
    db.commit()

    return {"message": "Ejercicio eliminado"}
