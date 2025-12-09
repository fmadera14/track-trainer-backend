from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db

from src.auth.dependencies import get_current_user
from src.session_exercises.models import SessionExercises
from src.sets.models import Set
from src.sets.schemas import SetCreate
from src.user.models import User
from src.workout_session.models import WorkoutSession

router = APIRouter()


@router.post("/{session_id}/{exercise_id}")
async def add_set_to_session_exercise(
    session_id: int,
    exercise_id: int,
    data: SetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validar que exista el session_exercise y pertenece al usuario
    session_exercise = (
        db.query(SessionExercises)
        .join(WorkoutSession)
        .filter(
            SessionExercises.session_id == session_id,
            SessionExercises.exercise_id == exercise_id,
            WorkoutSession.user_id == current_user.id,
        )
        .first()
    )

    if not session_exercise:
        raise HTTPException(status_code=404, detail="Session exercise not found")

    new_set = Set(
        session_exercise_id=session_exercise.id,
        set_number=data.set_number,
        reps=data.reps,
        weight=data.weight,
        unit=data.unit,
    )

    db.add(new_set)
    db.commit()
    db.refresh(new_set)

    return new_set
