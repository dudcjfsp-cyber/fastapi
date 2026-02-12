from fastapi import APIRouter
from services.user_service import get_all_members, get_member, get_ootd

router = APIRouter()

@router.get("/members")
def read_all_members():
    return get_all_members()

@router.get("/members/{username}")
def read_member_detail(username: str):
    member = get_member(username)
    if not member:
        return {"error": "팀원을 찾을 수 없습니다."}
    return member

@router.get("/ootd")
def read_ootd(day: str):
    outfit = get_ootd(day)
    if not outfit:
        return {"error": "기록된 코디가 없습니다."}
    return {"day": day, "outfit": outfit}
