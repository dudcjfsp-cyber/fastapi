import os
import base64
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google import genai
from fastmcp import Client
import uvicorn

# ──────────────────────────────────────────────
# 로깅 설정
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 환경 설정
# ──────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MCP_SERVER_URL = "http://localhost:8002/sse"

if not GEMINI_API_KEY:
    logger.warning("⚠️ GEMINI_API_KEY 가 설정되지 않았습니다. .env 파일을 확인하세요.")

# ──────────────────────────────────────────────
# FastAPI 앱 생성
# ──────────────────────────────────────────────
app = FastAPI(title="AI Stylist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_INSTRUCTION = """\
당신은 최고의 AI 패션 스타일리스트입니다.

[작업 흐름]
1. 먼저 제공된 도구(tools)를 사용하여 해당 팀원의 정보(이름, 성별, 스타일, 지역)를 조회하세요.
2. 조회한 정보와 사용자가 제공한 조건(날씨, 계절, 요일 등)을 종합하여 구체적인 옷차림을 추천하세요.
3. 추천은 항상 구체적이고 감각적으로 작성하세요. (예: "네이비 울 코트 + 크림색 터틀넥 + 슬림핏 블랙 팬츠")

[규칙]
- 팀원 정보 조회 시 반드시 도구를 사용하세요.
- 패션 추천은 조회한 정보를 바탕으로 창의적으로 생성하세요.
- 한국어로 답변하세요.
"""

# ──────────────────────────────────────────────
# 요청/응답 모델
# ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    include_image: bool = False

# ──────────────────────────────────────────────
# Gemini 클라이언트 (전역 싱글톤)
# ──────────────────────────────────────────────
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ──────────────────────────────────────────────
# 모델 선택 로직 (agent.py의 get_best_model 이식)
# ──────────────────────────────────────────────
PREFERRED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-flash-latest",
]

async def get_best_model() -> str:
    """사용 가능한 모델 중 우선순위가 가장 높은 모델을 반환합니다."""
    logger.info("🔍 사용 가능한 모델 검색 중...")
    try:
        available = []
        all_models_pager = await gemini_client.aio.models.list()
        async for m in all_models_pager:
            # 새 SDK(google-genai)와 구 SDK(google-generativeai) 호환
            methods = getattr(m, 'supported_generation_methods', None) or []
            model_id = m.name.replace("models/", "") if hasattr(m, 'name') else str(m)

            # generateContent 지원 모델만 필터링
            # 새 SDK에서 속성이 없으면 이름 기반으로 gemini 모델 수집
            if methods:
                if 'generateContent' in methods:
                    available.append(model_id)
            elif 'gemini' in model_id.lower():
                available.append(model_id)

        logger.info(f"📋 검색된 모델: {available}")

        # 우선순위 목록에서 먼저 매칭되는 모델 선택
        for pref in PREFERRED_MODELS:
            if pref in available:
                logger.info(f"✨ 선택된 모델: {pref}")
                return pref

        # 우선순위에 없으면 첫 번째 사용 가능 모델
        if available:
            logger.warning(f"⚠️ 우선순위 모델 없음. 대체 모델 사용: {available[0]}")
            return available[0]

    except Exception as e:
        logger.error(f"❌ 모델 검색 실패: {e}")

    logger.warning("⚠️ 기본 모델로 fallback: gemini-2.0-flash")
    return "gemini-2.0-flash"


# ──────────────────────────────────────────────
# API 엔드포인트
# ──────────────────────────────────────────────
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """React에서 질문을 받아 Gemini Agent를 실행하고 결과를 반환합니다."""
    logger.info(f"📨 요청 받음: {request.query} (이미지: {request.include_image})")

    try:
        mcp_client = Client(MCP_SERVER_URL)

        async with mcp_client:
            logger.info("✅ MCP 서버 연결 성공")
            session = mcp_client.session

            # (1) 텍스트 생성 ─ 동적 모델 선택
            selected_model = await get_best_model()
            response = await gemini_client.aio.models.generate_content(
                model=selected_model,
                contents=request.query,
                config=genai.types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0,
                    tools=[session],
                ),
            )
            response_text = response.text
            logger.info(f"✅ 텍스트 생성 완료 (모델: {selected_model}, 길이: {len(response_text or '')})")

            # (2) 이미지 생성 (선택적)
            generated_image_b64 = None
            if request.include_image:
                try:
                    logger.info("🎨 이미지 생성 시도 (imagen-3.0-generate-001)...")
                    image_response = await gemini_client.aio.models.generate_images(
                        model="imagen-3.0-generate-001",
                        prompt=f"Fashion illustration, full body outfit: {response_text[:300]}",
                        config=genai.types.GenerateImagesConfig(
                            number_of_images=1,
                        ),
                    )
                    if image_response.generated_images:
                        raw = image_response.generated_images[0].image.image_bytes
                        generated_image_b64 = base64.b64encode(raw).decode("utf-8")
                        logger.info("✅ 이미지 생성 성공")
                except Exception as img_err:
                    logger.error(f"⚠️ 이미지 생성 실패 (텍스트는 정상 반환): {img_err}")

            return {"response": response_text, "image": generated_image_b64}

    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """서버 상태 확인용"""
    return {"status": "ok", "mcp_server": MCP_SERVER_URL}


if __name__ == "__main__":
    logger.info("🚀 AI Stylist API 서버 시작 (포트: 8004)")
    uvicorn.run(app, host="0.0.0.0", port=8004)
