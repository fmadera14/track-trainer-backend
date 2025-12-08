from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

# Cargar variables de entorno del archivo .env
load_dotenv()

# Datos de conexión desde variables de entorno
DATABASE_USER = os.getenv("DB_USER")
DATABASE_PASSWORD = os.getenv("DB_PASSWORD")
DATABASE_HOST = os.getenv("DB_HOST", "localhost")
DATABASE_PORT = os.getenv("DB_PORT", 5432)
DATABASE_NAME = os.getenv("DB_NAME")

# URL de conexión a PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?sslmode=require"

# Crear engine SQLAlchemy
engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


# Dependencia para obtener sesión DB en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from src.user.models import User
from src.exercise.models import Exercise
