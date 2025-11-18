from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class BookResponse(BookBase):
    id: int
    author_id: int
    created_at: datetime
    likes_count: int = 0
    dislikes_count: int = 0
    rating: float = 0.0

    class Config:
        from_attributes = True