from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.routes import router as auth_router
from src.exercise.routes import router as exercise_router
from src.sets.routes import router as sets_router
from src.user.routes import router as user_router
from src.workout_session.routes import router as workout_session_router

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://v0-frontend.com",  # Agrega tu dominio real aquí
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos: GET, POST, PUT, DELETE...
    allow_headers=["*"],  # Permite todos los headers (incluye Authorization)
)

app.include_router(auth_router, prefix="/v1/auth", tags=["Auth"])
app.include_router(exercise_router, prefix="/v1/exercise", tags=["Exercise"])
app.include_router(sets_router, prefix="/v1/set", tags=["Sets"])
app.include_router(user_router, prefix="/v1/user", tags=["User"])
app.include_router(
    workout_session_router, prefix="/v1/workout-session", tags=["Workout Session"]
)
