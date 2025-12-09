from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base


class SessionExercises(Base):
    __tablename__ = "session_exercises"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer, ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id = Column(
        Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    order_index = Column(Integer, nullable=False)

    session = relationship("WorkoutSession", back_populates="session_exercises")
    exercise = relationship("Exercise", back_populates="session_exercises")
    sets = relationship(
        "Set",
        back_populates="session_exercise",
        cascade="all, delete",
        passive_deletes=True,
    )
