import math
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from board_database import get_db
from board_models import Post, Comment
from board_schemas import (
    PostCreate, PostUpdate, PostDelete, PostDetail,
    PostSummary, PostListResponse,
    CommentCreate
)

router = APIRouter(prefix="/api/v1", tags=["board"])

POSTS_PER_PAGE = 15


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ─── 게시글 API ───

@router.get("/posts", response_model=PostListResponse)
def list_posts(
    page: int = Query(1, ge=1),
    search: str = Query(""),
    db: Session = Depends(get_db),
):
    """게시글 목록 조회 (최신순, 페이지네이션, 검색)"""
    query = db.query(Post)
    if search:
        query = query.filter(or_(Post.title.contains(search), Post.content.contains(search)))

    total = query.count()
    total_pages = max(1, math.ceil(total / POSTS_PER_PAGE))
    offset = (page - 1) * POSTS_PER_PAGE
    posts = query.order_by(Post.created_at.desc()).offset(offset).limit(POSTS_PER_PAGE).all()

    summaries = [
        PostSummary(
            id=p.id, title=p.title, author=p.author,
            view_count=p.view_count, comment_count=len(p.comments),
            created_at=p.created_at,
        ) for p in posts
    ]
    return PostListResponse(posts=summaries, total=total, page=page, total_pages=total_pages)


@router.post("/posts", status_code=201)
def create_post(data: PostCreate, db: Session = Depends(get_db)):
    """게시글 생성"""
    post = Post(title=data.title, content=data.content, author=data.author, password=hash_password(data.password))
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"msg": "게시글이 작성되었습니다.", "id": post.id}


@router.get("/posts/{post_id}", response_model=PostDetail)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """게시글 상세 조회 + 조회수 증가"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    post.view_count += 1
    db.commit()
    db.refresh(post)
    return post


@router.patch("/posts/{post_id}")
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    """게시글 수정 (비밀번호 확인)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if not verify_password(data.password, post.password):
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content
    db.commit()
    return {"msg": "게시글이 수정되었습니다."}


@router.delete("/posts/{post_id}")
def delete_post(post_id: int, data: PostDelete, db: Session = Depends(get_db)):
    """게시글 삭제 (비밀번호 확인)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if not verify_password(data.password, post.password):
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    db.delete(post)
    db.commit()
    return {"msg": "게시글이 삭제되었습니다."}


# ─── 댓글 API ───

@router.post("/posts/{post_id}/comments", status_code=201)
def create_comment(post_id: int, data: CommentCreate, db: Session = Depends(get_db)):
    """댓글 작성"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    comment = Comment(post_id=post_id, author=data.author, content=data.content, password=hash_password(data.password))
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"msg": "댓글이 작성되었습니다.", "id": comment.id}


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, data: PostDelete, db: Session = Depends(get_db)):
    """댓글 삭제 (비밀번호 확인)"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    if not verify_password(data.password, comment.password):
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    db.delete(comment)
    db.commit()
    return {"msg": "댓글이 삭제되었습니다."}
