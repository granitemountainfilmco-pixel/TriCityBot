@echo off
SETLOCAL EnableDelayedExpansion

:: Get the directory where this script is located
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

echo [1/4] Detecting Directory: %ROOT_DIR%

:: 1. Start Ollama (Hidden)
echo [2/4] Starting Ollama...
start /min "" ollama serve

:: 2. Setup and Start Backend
echo [3/4] Initializing Backend...
cd /d "%ROOT_DIR%backend"
if not exist "venv" (
    echo Creating Python Virtual Environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Updating Backend Requirements...
pip install -r requirements.txt --quiet

:: CRITICAL CHANGE: Use 'start' to run the backend in a NEW window
echo Launching Backend Server...
start "ShopOS-Backend-Server" cmd /k "venv\Scripts\activate && python main.py"

:: 3. Setup and Start Frontend
echo [4/4] Initializing Frontend...
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" (
    echo Installing Node Modules...
    call npm install
)

:: CRITICAL CHANGE: Use 'start' to run the frontend in a NEW window
echo Launching Frontend Server...
start "ShopOS-Frontend-Vite" cmd /k "npm run dev"

:: 4. Final Launch
echo Everything is launching. Waiting 8 seconds for servers to warm up...
timeout /t 8
start chrome http://localhost:5173
