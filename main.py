from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Services for warm-up
from services.shop_service import get_items

# Routers
from routers import users, courses, appeals, shop, auth

# [NEW] 서버 시작 시 미리 데이터 로딩 (Warm-up)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔥 Warming up Shop Cache...")
    try:
        get_items() # 서버 시작 시 아이템 목록 미리 로딩
        print("✅ Shop Cache Ready!")
    except Exception as e:
        print(f"⚠️ Cache Warmup Failed: {e}")
    yield
    print("🛑 Server Shutting Down...")

app = FastAPI(
    title="나만의 API (Refactored)",
    description="Refactored Modular API with Routers and Services",
    version="0.2.0",
    lifespan=lifespan
)

import os

# CORS 허용 Origin 목록 (프론트엔드 개발 서버 + 백엔드 서버들)
ALLOWED_ORIGINS = [
    "http://localhost:5173",   # React 프론트엔드 (Vite 기본 포트)
    "http://localhost:8000",   # FastAPI 백엔드
    "http://localhost:8002",   # MCP 서버
    "http://localhost:8004",   # API 서버
]

# 환경변수로 추가 origin 설정 가능 (쉼표 구분)
extra_origins = os.getenv("CORS_ORIGINS", "")
if extra_origins:
    ALLOWED_ORIGINS.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ─── 글로벌 예외 처리기 (통일된 에러 응답) ───

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic 유효성 검사 실패 시 통일된 형식으로 응답"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"]
        })
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "유효성 검사 실패",
            "detail": errors
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """처리되지 않은 모든 예외를 통일된 형식으로 응답"""
    # MySQL 에러인 경우
    error_type = type(exc).__name__
    if "mysql" in type(exc).__module__ if hasattr(type(exc), '__module__') else False:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "데이터베이스 오류",
                "detail": str(exc)
            }
        )
    
    # 일반 비즈니스 로직 에러
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": error_type,
            "detail": str(exc)
        }
    )

# 1. 가게 간판 달기
@app.get("/")
def read_root():
    return {"message": "안녕하세요 (Refactored Version)"}

# 2. 라우터 등록
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(appeals.router)
app.include_router(shop.router)
app.include_router(auth.router)
