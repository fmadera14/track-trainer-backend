from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import aliased, Session

from config.database import get_db
from src.auth.dependencies import get_current_user
from src.user.models import User
from src.workout_session.models import WorkoutSession
from src.workout_session.schema import WorkoutSessionCreate, WorkoutSessionRead
from src.session_exercises.models import SessionExercises
from src.exercise.models import Exercise

router = APIRouter()


@router.get("/")
async def list_sessions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    workout_sessions = (
        db.query(WorkoutSession).filter(WorkoutSession.user_id == current_user.id).all()
    )
    return workout_sessions


@router.get("/{session_id}")
async def detail_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    exercises = (
        db.query(Exercise)
        .join(SessionExercises, SessionExercises.exercise_id == Exercise.id)
        .filter(SessionExercises.session_id == session_id)
        .all()
    )

    return {
        "session": session,
        "exercises": exercises,
    }


@router.post("/")
async def create_session(
    session_data: WorkoutSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_session = WorkoutSession(
        user_id=current_user.id,
        name=session_data.name,
        notes=session_data.notes,
        session_date=session_data.session_date,
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@router.put("/{session_id}")
async def edit_work_session(
    session_id: int,
    session_data: WorkoutSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session_exists = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.name == session_data.name,
            WorkoutSession.user_id == current_user.id,
        )
        .first()
    )

    if session_exists and session_data.name != session_exists.name:
        raise HTTPException(
            status_code=400, detail="El nombre de la sesión ya está en uso"
        )

    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id, WorkoutSession.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="No se encontró el ejercicio")

    session.name = session_data.name
    session.notes = session_data.notes
    session.session_date = session_data.session_date

    db.commit()
    db.refresh(session)

    return session
