from pydantic import BaseModel
from typing import Optional

from app.schemas.user import User


class Token(BaseModel):
    """
    Schema for token response.
    """
    access_token: str
    token_type: str
    user: User


class TokenPayload(BaseModel):
    """
    Schema for token payload.
    """
    sub: Optional[int] = None 