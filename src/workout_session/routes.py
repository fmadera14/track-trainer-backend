from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from src.auth.dependencies import get_current_user
from src.user.models import User
from src.workout_session.models import WorkoutSession
from src.workout_session.schema import WorkoutSessionCreate, WorkoutSessionRead

router = APIRouter()


@router.get("/")
async def list_sessions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    workout_sessions = (
        db.query(WorkoutSession).filter(WorkoutSession.user_id == current_user.id).all()
    )
    return workout_sessions


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
