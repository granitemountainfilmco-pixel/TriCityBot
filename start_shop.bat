@echo off
set "ROOT_DIR=%~dp0"

:: 1. Start Ollama
start /min "" ollama serve

:: 2. Backend Setup
echo [BACKEND] Starting...
cd /d "%ROOT_DIR%backend"
if not exist "venv" python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt --quiet
start "ShopOS-Backend" cmd /k "venv\Scripts\activate && python main.py"

:: 3. Frontend Setup
echo [FRONTEND] Starting...
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" call npm install
:: Clear old vite cache to fix the blank screen
if exist "node_modules\.vite" rmdir /s /q "node_modules\.vite"
start "ShopOS-Frontend" cmd /k "npm run dev -- --force"

:: 4. Launch
timeout /t 8
start chrome http://localhost:5173
