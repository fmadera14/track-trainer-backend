from pydantic import BaseModel
from enum import Enum


class WeightUnit(str, Enum):
    lb = "lb"
    kg = "kg"


class SetCreate(BaseModel):
    set_number: int
    reps: int
    weight: float
    unit: WeightUnit


class SetUpdate(BaseModel):
    set_number: int
    reps: int
    weight: float
    unit: WeightUnit
