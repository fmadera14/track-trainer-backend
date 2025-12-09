from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(150), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    session_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="workout_session")
    session_exercises = relationship("SessionExercises", back_populates="session")
