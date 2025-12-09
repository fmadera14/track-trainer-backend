from pydantic import BaseModel, Field
from datetime import date


class WorkoutSessionCreate(BaseModel):
    name: str = Field(..., min_length=3)
    notes: str | None = None
    session_date: date


class WorkoutSessionRead(BaseModel):
    id: int
    name: str
    notes: str | None
    session_date: date
    created_at: str

    class Config:
        orm_mode = True


class AddExercises(BaseModel):
    exercise_ids: list[int]


class UpdateOrder(BaseModel):
    exercise_ids: list[int]
