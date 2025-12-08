from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    username = Column(String(30), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP)
    last_login = Column(TIMESTAMP)
    active = Column(Boolean, default=False)
