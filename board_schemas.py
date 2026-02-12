from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=4)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    password: str = Field(..., min_length=1)


class PostDelete(BaseModel):
    password: str = Field(..., min_length=1)


class PostSummary(BaseModel):
    id: int
    title: str
    author: str
    view_count: int
    comment_count: int = 0
    created_at: datetime
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    id: int
    author: str
    content: str
    created_at: datetime
    class Config:
        from_attributes = True


class PostDetail(BaseModel):
    id: int
    title: str
    content: str
    author: str
    view_count: int
    created_at: datetime
    comments: List[CommentResponse] = []
    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    posts: List[PostSummary]
    total: int
    page: int
    total_pages: int


class CommentCreate(BaseModel):
    author: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1)
    password: str = Field(..., min_length=4)
