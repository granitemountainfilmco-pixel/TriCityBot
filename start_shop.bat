@echo off
set "ROOT_DIR=%~dp0"

:: 1. Start Ollama
start /min "" ollama serve

:: 2. Backend Setup & Launch
echo [BACKEND] Checking environment...
cd /d "%ROOT_DIR%backend"
if not exist "venv" (
    echo [BACKEND] Creating Virtual Environment...
    python -m venv venv
)
:: Call install in the current window to ensure it's done before launching
call venv\Scripts\activate
echo [BACKEND] Installing/Updating Requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt --quiet
:: Now launch the actual server in a new window
start "ShopOS-Backend" cmd /k "cd /d %ROOT_DIR%backend && venv\Scripts\activate && python main.py"

:: 3. Frontend Setup & Launch
echo [FRONTEND] Checking Node modules...
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" (
    echo [FRONTEND] Installing dependencies (this may take a minute)...
    call npm install
)
:: Launch Vite with --force to clear cache
start "ShopOS-Frontend" cmd /k "cd /d %ROOT_DIR%frontend && npm run dev -- --force"

:: 4. Final Launch
echo Everything is starting up...
timeout /t 8
start chrome http://localhost:5173
