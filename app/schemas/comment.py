from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    parent_id: Optional[int] = None

class CommentResponse(CommentBase):
    id: int
    user_id: int
    created_at: datetime
    replies: List['CommentResponse'] = Field(default_factory=list)

    class Config:
        from_attributes = True
