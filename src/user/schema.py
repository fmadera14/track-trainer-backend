from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3)
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)


class UserRead(BaseModel):
    id: int
    name: str
    username: str
    active: bool

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    name: str
    username: str

    class Config:
        orm_mode = True


class UserEdit(BaseModel):
    name: str
    username: str
    email: str
