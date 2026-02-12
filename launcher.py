import subprocess
import os
import time

# 현재 파일이 있는 디렉토리 (fastapi-hello)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 프론트엔드 경로 (한글 경로 처리)
FRONTEND_DIR = os.path.join(BASE_DIR, "리액트실습", "리액트실습")

def run_in_new_window(title, command, cwd=BASE_DIR):
    """새로운 CMD 창에서 명령어 실행"""
    print(f"🚀 Starting {title}...")
    # Windows `start` 명령어로 새 창 띄우기
    # title은 따옴표로 감싸야 함
    subprocess.Popen(f'start "{title}" cmd /k "{command}"', shell=True, cwd=cwd)

def main():
    print("=== AI Stylist 서비스 시작 ===")
    
    # 1. FastAPI Main (8000)
    run_in_new_window("FastAPI Main (8000)", "uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    time.sleep(2) # 포트 충돌 방지 대기

    # 2. MCP Server (8002)
    run_in_new_window("MCP Server (8002)", "fastmcp run server_mcp.py --transport sse --port 8002")

    # 3. API Server (8004) - 재시작 루프 포함
    # batch의 for loop 문법: python string에서는 %x (배치파일 아님)
    loop_cmd = "for /l %x in (1, 1, 100) do ( echo Starting API Server... & python api_server.py & echo Server crashed! Restarting in 3 seconds... & timeout /t 3 )"
    run_in_new_window("API Server (8004)", loop_cmd)

    # 4. Frontend (5173)
    if os.path.exists(FRONTEND_DIR):
        run_in_new_window("Frontend (5173)", "npm run dev", cwd=FRONTEND_DIR)
    else:
        print(f"❌ Error: Frontend directory not found at {FRONTEND_DIR}")

    print("\n✅ 모든 서버 실행 명령을 전송했습니다.")

if __name__ == "__main__":
    main()
