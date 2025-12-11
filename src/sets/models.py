from sqlalchemy import Column, Enum, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship
from config.database import Base
from src.sets.schemas import WeightUnit


class Set(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    session_exercise_id = Column(
        Integer, ForeignKey("session_exercises.id", ondelete="CASCADE"), nullable=False
    )
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=True)
    unit = Column(Enum(WeightUnit, name="weight_unit"), nullable=False)
    order_index = Column(Integer, nullable=False)

    session_exercise = relationship("SessionExercises", back_populates="sets")
