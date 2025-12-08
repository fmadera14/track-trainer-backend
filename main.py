from fastapi import FastAPI

from src.auth.routes import router as auth_router
from src.user.routes import router as user_router
from src.exercise.routes import router as exercise_router
from src.workout_session.routes import router as workout_session_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(exercise_router, prefix="/exercise", tags=["Exercise"])
app.include_router(
    workout_session_router, prefix="/workout-session", tags=["Workout Session"]
)
