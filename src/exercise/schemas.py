from pydantic import BaseModel, Field


class ExerciseCreate(BaseModel):
    name: str = Field(..., min_length=3)
    description: str | None = Field(default=None)
    muscle_group: str | None = Field(default=None)


class ExerciseUpdate(BaseModel):
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    muscle_group: str | None = Field(default=None)
