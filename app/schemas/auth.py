from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    exp: Optional[int] = None

class TokenPayload(BaseModel):
    sub: Optional[int] = None

class UserInfo(BaseModel):
    id: int
    email: str
    name: str
    role: str

class LoginResponse(BaseModel):
    token: str
    user: UserInfo 