from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PredictionRequest(BaseModel):
    text: str
    model_type: Literal["basic", "medium", "premium"] = Field(
        default="basic",
        example="basic",
        description="Доступные модели: basic, medium, premium"
    )
