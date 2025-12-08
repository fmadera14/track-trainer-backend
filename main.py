from fastapi import FastAPI

from src.auth.routes import router as auth_router
from src.user.routes import router as user_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/user", tags=["User"])
