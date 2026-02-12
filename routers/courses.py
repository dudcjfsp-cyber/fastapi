from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.course_service import get_all_courses, register_student
from routers.auth import get_current_user

router = APIRouter()

class RegistrationRequest(BaseModel):
    course_id: int

@router.get("/courses")
def read_courses():
    """개설된 강좌 목록을 반환합니다."""
    return get_all_courses()

@router.post("/registrations")
def register_course_endpoint(request: RegistrationRequest, user = Depends(get_current_user)):
    """수강신청을 처리합니다."""
    return register_student(user['username'], request.course_id)
