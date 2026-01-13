@echo off
set "ROOT_DIR=%~dp0"

:: 1. Start Ollama AI
start "" ollama serve

:: 2. Backend Setup & Start
echo [BACKEND] Checking paths...
if not exist "%ROOT_DIR%backend" (
    echo Error: 'backend' folder not found!
    pause
    exit /b
)
cd /d "%ROOT_DIR%backend"
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt --quiet
start "ShopOS-Backend" cmd /k "venv\Scripts\activate && python main.py"

:: 3. Frontend Setup & Start
echo [FRONTEND] Checking paths...
if not exist "%ROOT_DIR%frontend" (
    echo Error: 'frontend' folder not found!
    pause
    exit /b
)
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)
:: Clean the cache to fix the blank screen issue
if exist "node_modules\.vite" rmdir /s /q "node_modules\.vite"
start "ShopOS-Frontend" cmd /k "npm run dev -- --force"

:: 4. Launch Browser
echo Launching Shop OS...
timeout /t 8
start chrome http://localhost:5173
