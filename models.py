from pydantic import BaseModel
from typing import Optional

class UserCredentials(BaseModel):
    username: str
    password: str

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

class ItemCreate(BaseModel):
    id:          Optional[int] = None   # ← must be here
    name:        str
    description: Optional[str] = None
    price:       float

    class Config:
        extra = "ignore"   # ← (this is the default, but just to be explicit)
