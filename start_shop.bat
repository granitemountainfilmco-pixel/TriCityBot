@echo off
SETLOCAL EnableDelayedExpansion
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

:: 1. Start Ollama
start /min "" ollama serve

:: 2. Backend (Corrected Path)
cd /d "%ROOT_DIR%backend"
if not exist "venv" python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt --quiet
start "ShopOS-Backend" cmd /k "python main.py"

:: 3. Frontend (Corrected Path)
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" call npm install
start "ShopOS-Frontend" cmd /k "npm run dev"

:: 4. Launch
timeout /t 8
start chrome http://localhost:5173
