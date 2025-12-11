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
    order_index: int


class SetUpdate(BaseModel):
    set_number: int
    reps: int
    weight: float
    unit: WeightUnit
    order_index: int


class SetOrderItem(BaseModel):
    set_id: int
    order_index: int


class ReorderSetsRequest(BaseModel):
    orders: list[SetOrderItem]
