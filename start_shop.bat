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
echo Installing/Updating Backend Requirements...
pip install -r requirements.txt --quiet
start "ShopOS-Backend" cmd /k "python main.py"

:: 3. Setup and Start Frontend
echo [4/4] Initializing Frontend...
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" (
    echo Installing Node Modules (this may take a minute)...
    call npm install
)
start "ShopOS-Frontend" cmd /k "npm run dev"

:: 4. Final Launch
echo Everything is launching. Waiting for servers...
timeout /t 8
start chrome http://localhost:5173
