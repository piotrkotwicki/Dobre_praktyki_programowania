from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    roles: Optional[List[str]] = ["ROLE_USER"]

class LoginData(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str
    exp: Optional[int] = None
    roles: List[str] = []

class UserDetails(BaseModel):
    username: str
    roles: List[str]

    class Config:
        from_attributes = True