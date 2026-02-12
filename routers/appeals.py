from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.course_service import get_enrollments, delete_enrollment
from services.appeal_service import create_appeal, get_appeals
from routers.auth import get_current_user, get_admin_user

router = APIRouter()

# ─── 관리자 전용 기능 (ADMIN only) ───

@router.get("/courses/{course_id}/enrollments")
def read_enrollments_endpoint(course_id: int, admin = Depends(get_admin_user)):
    """수강생 목록 조회 (관리자용)"""
    return get_enrollments(course_id)

@router.delete("/enrollments/{enrollment_id}")
def cancel_enrollment_endpoint(enrollment_id: int, admin = Depends(get_admin_user)):
    """수강취소 (관리자용)"""
    return delete_enrollment(enrollment_id)

# ─── 이의신청 ───

class AppealRequest(BaseModel):
    course_id: int
    content: str
    is_secret: bool = True

@router.post("/appeals")
def create_appeal_endpoint(request: AppealRequest, user = Depends(get_current_user)):
    """이의신청 등록"""
    return create_appeal(request.course_id, user['username'], request.content, request.is_secret)

@router.get("/courses/{course_id}/appeals")
def read_appeals_endpoint(course_id: int):
    """이의신청 목록 조회"""
    return get_appeals(course_id)
