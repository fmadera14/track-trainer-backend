from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from src.auth.dependencies import get_current_user
from src.user.models import User
from src.workout_session.models import WorkoutSession
from src.workout_session.schema import (
    AddExercises,
    UpdateOrder,
    RemoveExercises,
    WorkoutSessionCreate,
)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    # Traer ejercicios + sets
    session_exercises = (
        db.query(SessionExercises)
        .join(Exercise, Exercise.id == SessionExercises.exercise_id)
        .filter(SessionExercises.session_id == session_id)
        .order_by(SessionExercises.order_index.asc())
        .all()
    )

    # Formar respuesta completa
    exercises_output = []
    for se in session_exercises:
        exercises_output.append(
            {
                "id": se.exercise.id,
                "name": se.exercise.name,
                "description": se.exercise.description,
                "session_exercise_id": se.id,
                "order_index": se.order_index,
                "sets": [
                    {
                        "id": s.id,
                        "set_number": s.set_number,
                        "reps": s.reps,
                        "weight": s.weight,
                        "unit": s.unit.value,
                    }
                    for s in se.sets
                ],
            }
        )

    return {
        "id": session.id,
        "user_id": session.user_id,
        "name": session.name,
        "notes": session.notes,
        "created_at": session.created_at,
        "session_date": session.session_date,
        "exercises": exercises_output,
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


@router.post("/{session_id}/add-exercises")
async def add_exercises_to_session(
    session_id: int,
    data: AddExercises,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. verificar que la sesión existe
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    # 2. obtener los ejercicios
    exercises = db.query(Exercise).filter(Exercise.id.in_(data.exercise_ids)).all()

    if len(exercises) != len(data.exercise_ids):
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail="One or more exercise IDs do not exist",
        )

    # 3. evitar duplicados
    existing = (
        db.query(SessionExercises.exercise_id)
        .filter(SessionExercises.session_id == session_id)
        .all()
    )
    existing_ids = {e[0] for e in existing}

    new_ids = [eid for eid in data.exercise_ids if eid not in existing_ids]

    # 4. obtener el último order_index
    last_order = (
        db.query(SessionExercises)
        .filter(SessionExercises.session_id == session_id)
        .order_by(SessionExercises.order_index.desc())
        .first()
    )

    next_index = last_order.order_index + 1 if last_order else 1

    # 5. insertar ejercicios con order_index
    for exercise_id in new_ids:
        link = SessionExercises(
            session_id=session_id,
            exercise_id=exercise_id,
            order_index=next_index,
        )
        next_index += 1
        db.add(link)

    db.commit()

    return {
        "session_id": session_id,
        "added_exercises": new_ids,
        "skipped_duplicates": list(existing_ids.intersection(data.exercise_ids)),
    }


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
            status_code=status.HTTP_400_NOT_FOUND,
            detail="El nombre de la sesión ya está en uso",
        )

    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id, WorkoutSession.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el ejercicio"
        )

    session.name = session_data.name
    session.notes = session_data.notes
    session.session_date = session_data.session_date

    db.commit()
    db.refresh(session)

    return session


@router.put("/{session_id}/reorder")
async def reorder_session_exercises(
    session_id: int,
    data: UpdateOrder,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. verificar que la sesión existe y pertenece al usuario
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    # 2. obtener los ejercicios reales en esta sesión
    session_exercises = (
        db.query(SessionExercises)
        .filter(SessionExercises.session_id == session_id)
        .all()
    )

    current_ids = {se.exercise_id for se in session_exercises}

    # 3. validar que los enviados coinciden con los actuales
    if set(data.exercise_ids) != current_ids:
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail="Exercise list does not match current session exercises",
        )

    # 4. actualizar order_index según el nuevo orden
    for new_index, exercise_id in enumerate(data.exercise_ids, start=1):
        db.query(SessionExercises).filter(
            SessionExercises.session_id == session_id,
            SessionExercises.exercise_id == exercise_id,
        ).update({"order_index": new_index})

    db.commit()

    return {
        "session_id": session_id,
        "new_order": data.exercise_ids,
    }


@router.delete("/{session_id}/remove-exercises")
async def remove_exercises_from_session(
    session_id: int,
    data: RemoveExercises,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. verificar sesión
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id,
            WorkoutSession.user_id == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    # 2. obtener solo ejercicios que estén realmente en la sesión
    existing_links = (
        db.query(SessionExercises)
        .filter(
            SessionExercises.session_id == session_id,
            SessionExercises.exercise_id.in_(data.exercise_ids),
        )
        .all()
    )

    if not existing_links:
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail="None of the provided exercises are in this session",
        )

    removed_ids = [link.exercise_id for link in existing_links]

    # 3. eliminar vínculos
    for link in existing_links:
        db.delete(link)

    db.commit()

    # 4. Reordenar order_index para no dejar huecos
    remaining = (
        db.query(SessionExercises)
        .filter(SessionExercises.session_id == session_id)
        .order_by(SessionExercises.order_index.asc())
        .all()
    )

    for idx, link in enumerate(remaining, start=1):
        link.order_index = idx

    db.commit()

    return {
        "session_id": session_id,
        "removed_exercises": removed_ids,
        "remaining_count": len(remaining),
    }


@router.delete("/{session_id}")
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(WorkoutSession)
        .filter(
            WorkoutSession.id == session_id, WorkoutSession.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workout session not found"
        )

    db.delete(session)
    db.commit()

    return {"detail": "Workout session deleted succesfully"}
