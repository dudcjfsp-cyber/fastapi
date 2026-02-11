from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data import get_ootd, get_all_members, get_member

app = FastAPI(
    title="나만의 API",
    description="이것은 나만의 API입니다.",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 가게 간판 달기
@app.get("/")
# 2. 경로(Path) 설정: 정문으로 들어오면
def read_root():
    return {"message": "안녕하세요"}
# 3. JSON 응답 (자동 변환!)

# 5. Parameter 1: 경로 변수
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": "명품 시계"}

# 6. Parameter 2: 옵션 변수
@app.get("/ootd")
def read_ootd(day: str):
    outfit = get_ootd(day)
    if not outfit:
        return {"error": "기록된 코디가 없습니다."}
    return {"day": day, "outfit": outfit}

# 7. [실습] '팀원 프로필' API 만들기
@app.get("/members")
def read_all_members():
    return get_all_members()

@app.get("/members/{username}")
def read_member_detail(username: str):
    member = get_member(username)
    if not member:
        return {"error": "팀원을 찾을 수 없습니다."}
    return member
