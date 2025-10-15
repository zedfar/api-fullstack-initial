from pydantic import BaseModel
from typing import Any, Dict

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer",
    metadata: Any | None = None

class TokenData(BaseModel):
    username: str | None = None
