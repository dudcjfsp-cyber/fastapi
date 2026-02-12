@echo off
echo Starting Services...

:: 1. Start FastAPI (Main) - Uses --reload for auto-restart on code change
start "FastAPI Main (8000)" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: 2. Start MCP Server - Uses fastmcp (assumed stable, but can loop if needed)
start "MCP Server (8002)" cmd /k "fastmcp run server_mcp.py --transport sse --port 8002"

:: 3. Start API Server (8004) - Custom loop for auto-restart on crash
start "API Server (8004)" cmd /k "for /l %%x in (1, 1, 100) do ( echo Starting API Server... & python api_server.py & echo Server crashed! Restarting in 3 seconds... & timeout /t 3 )"

:: 4. Start Frontend (Vite)
start "Frontend (5173)" cmd /k "cd 리액트실습/리액트실습 && npm run dev"

echo All servers attempted to start.
