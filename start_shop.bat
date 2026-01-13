@echo off
set "ROOT_DIR=%~dp0"

:: 1. Start Ollama
start /min "" ollama serve

:: 2. Backend
cd /d "%ROOT_DIR%backend"
if not exist "venv" python -m venv venv
call venv\Scripts\activate
pip install fastapi uvicorn ollama tavily-python pydantic --quiet
start "ShopOS-Backend" cmd /k "venv\Scripts\activate && python main.py"

:: 3. Frontend
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" call npm install
:: The --force flag clears the cached blank HTML error
start "ShopOS-Frontend" cmd /k "npm run dev -- --force"

:: 4. Launch
timeout /t 8
start chrome http://localhost:5173
