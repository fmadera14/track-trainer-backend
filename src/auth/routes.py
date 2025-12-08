from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.user.models import User
from src.user.schema import UserCreate, UserResponse
from config.database import get_db
from config.password_utils import verify_password
from config.security import create_access_token, hash_password

router = APIRouter()


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    token = create_access_token({"sub": user.username, "user_id": user.id})

    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # ¿Existe el usuario?
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo ya esta en uso")

    # Crear usuario nuevo
    new_user = User(
        name=user_data.name,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        email=user_data.email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
