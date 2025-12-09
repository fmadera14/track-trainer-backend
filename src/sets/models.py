from sqlalchemy import Column, Enum, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship
from config.database import Base
import enum


class WeightUnit(enum.Enum):
    lb = "lb"
    kg = "kg"


class Sets(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    session_exercise_id = Column(
        Integer, ForeignKey("session_exercises.id", ondelete="CASCADE"), nullable=False
    )
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=True)
    unit = Column(Enum(WeightUnit, name="weight_unit"), nullable=False)

    session_exercises = relationship("SessionExercises", back_populates="sets")
