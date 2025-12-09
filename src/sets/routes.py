from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db

from src.auth.dependencies import get_current_user
from src.session_exercises.models import SessionExercises
from src.sets.models import Set
from src.sets.schemas import SetCreate, SetUpdate
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


@router.put("/{set_id}")
async def edit_set(
    set_id: int,
    data: SetUpdate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    set = db.query(Set).filter(Set.id == set_id).first()

    if not set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Set not found"
        )

    set.reps = data.reps
    set.set_number = data.set_number
    set.unit = data.unit
    set.weight = data.weight

    db.commit()
    db.refresh(set)

    return {
        "id": set.id,
        "set_number": set.set_number,
        "reps": set.reps,
        "unit": set.unit,
        "weight": set.weight,
    }


@router.delete("/{set_id}")
async def delete_set():
    # TODO
    pass
