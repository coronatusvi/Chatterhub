from pydantic import BaseModel, EmailStr, Field

class RegisterSchema(BaseModel):
    username: str  = Field(..., min_length=3, max_length=20)
    email:    EmailStr
    password: str  = Field(..., min_length=6)

class LoginSchema(BaseModel):
    username: str
    password: str
    remember: bool | None = False