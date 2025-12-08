from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    username = Column(String(30), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP, server_default=func.now())
    active = Column(Boolean, default=False)

    exercises = relationship("Exercise", back_populates="user")
    workout_session = relationship("WorkoutSession", back_populates="user")
