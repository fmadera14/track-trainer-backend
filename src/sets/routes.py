from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db

from src.auth.dependencies import get_current_user
from src.session_exercises.models import SessionExercises
from src.sets.models import Set
from src.sets.schemas import SetCreate, SetUpdate, ReorderSetsRequest
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

    existing_set = (
        db.query(Set)
        .filter(
            Set.session_exercise_id == session_exercise.id,
            Set.order_index == data.order_index,
        )
        .first()
    )

    if existing_set:
        raise HTTPException(
            status_code=400,
            detail=f"order_index {data.order_index} is already in use for this exercise in this session",
        )

    new_set = Set(
        session_exercise_id=session_exercise.id,
        set_number=data.set_number,
        reps=data.reps,
        weight=data.weight,
        unit=data.unit,
        order_index=data.order_index,
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

    session_exercise = (
        db.query(SessionExercises)
        .filter(SessionExercises.id == set.session_exercise_id)
        .first()
    )

    if not session_exercise:
        raise HTTPException(status_code=404, detail="Session exercise not found")

    existing_set = (
        db.query(Set)
        .filter(
            Set.session_exercise_id == session_exercise.id,
            Set.order_index == data.order_index,
            Set.id != set_id,
        )
        .first()
    )

    if existing_set:
        raise HTTPException(
            status_code=400,
            detail=f"order_index {data.order_index} is already in use for this exercise in this session",
        )

    set.reps = data.reps
    set.set_number = data.set_number
    set.unit = data.unit
    set.weight = data.weight
    set.order_index = data.order_index

    db.commit()
    db.refresh(set)

    return {
        "id": set.id,
        "set_number": set.set_number,
        "reps": set.reps,
        "unit": set.unit,
        "weight": set.weight,
    }


@router.put("/reorder")
async def reorder_sets(
    payload: ReorderSetsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.orders:
        raise HTTPException(400, "Order list cannot be empty")

    set_ids = [item.set_id for item in payload.orders]
    new_order_indices = [item.order_index for item in payload.orders]

    # 1. Validar que no hayan order_index repetidos
    if len(new_order_indices) != len(set(new_order_indices)):
        raise HTTPException(400, "Duplicate order_index values are not allowed")

    # 2. Obtener los sets y validar que existan y sean del usuario
    sets = (
        db.query(Set)
        .join(SessionExercises, SessionExercises.id == Set.session_exercise_id)
        .join(WorkoutSession, WorkoutSession.id == SessionExercises.session_id)
        .filter(Set.id.in_(set_ids), WorkoutSession.user_id == current_user.id)
        .all()
    )

    if len(sets) != len(set_ids):
        raise HTTPException(404, "One or more sets not found or unauthorized")

    # 3. Validar que todos pertenezcan al mismo session_exercise
    session_exercise_ids = {s.session_exercise_id for s in sets}
    if len(session_exercise_ids) != 1:
        raise HTTPException(400, "All sets must belong to the same session exercise")

    # 4. Actualizar los order_index
    id_to_order = {item.set_id: item.order_index for item in payload.orders}

    for s in sets:
        s.order_index = id_to_order[s.id]

    db.commit()

    return {"detail": "Set order updated successfully"}


@router.delete("/{set_id}")
async def delete_set(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    set_to_delete = (
        db.query(Set)
        .join(SessionExercises, SessionExercises.id == Set.session_exercise_id)
        .join(WorkoutSession, WorkoutSession.id == SessionExercises.session_id)
        .filter(Set.id == set_id, WorkoutSession.user_id == current_user.id)
        .first()
    )

    if not set_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Set not found"
        )

    session_exercise_id = set_to_delete.session_exercise_id

    db.delete(set_to_delete)
    db.commit()

    remaining_sets = (
        db.query(Set)
        .filter(Set.session_exercise_id == session_exercise_id)
        .order_by(Set.order_index.asc())
        .all()
    )

    for index, s in enumerate(remaining_sets, start=1):
        s.order_index = index

    db.commit()

    return {"detail": "Set deleted and order_index updated successfully"}
