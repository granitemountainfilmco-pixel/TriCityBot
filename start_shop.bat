@echo off
set "ROOT_DIR=%~dp0"

:: 1. Start Ollama (Hidden)
start /min "" ollama serve

:: 2. Setup & Launch Backend in SEPARATE window
echo [BACKEND] Syncing environment...
cd /d "%ROOT_DIR%backend"
if not exist "venv" python -m venv venv
call venv\Scripts\activate
pip install fastapi uvicorn ollama tavily-python pydantic --quiet

:: Use 'start' to spawn a new window so this script can continue
start "ShopOS-Backend" cmd /k "cd /d %ROOT_DIR%backend && venv\Scripts\activate && python main.py"

:: 3. Setup & Launch Frontend in SEPARATE window
echo [FRONTEND] Syncing Node...
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" call npm install

:: Use 'start' to spawn a new window
start "ShopOS-Frontend" cmd /k "cd /d %ROOT_DIR%frontend && npm run dev -- --force"

:: 4. Final Launch (Now this will actually reach here!)
echo [SYSTEM] Waiting for servers to warm up...
timeout /t 8
start chrome http://localhost:5173
