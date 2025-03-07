from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    title: Optional[str] = None
    content: Optional[str] = None

class Post(PostBase):
    id: int
    author_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True 