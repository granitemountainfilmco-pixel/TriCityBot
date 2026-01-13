@echo off
set "ROOT_DIR=%~dp0"

:: 1. Start Ollama
start /min "" ollama serve

:: 2. Setup Backend
echo [BACKEND] Starting...
cd /d "%ROOT_DIR%backend"
call venv\Scripts\activate
pip install -r requirements.txt --quiet
start "ShopOS-Backend" cmd /k "venv\Scripts\activate && python main.py"

:: 3. Setup Frontend
echo [FRONTEND] Starting...
cd /d "%ROOT_DIR%frontend"
:: FIXED: Wipe the old cache which causes the blank screen
if exist "node_modules\.vite" rmdir /s /q "node_modules\.vite"
if not exist "node_modules" call npm install
:: Launch from the frontend folder specifically
start "ShopOS-Frontend" cmd /k "npm run dev -- --force"

:: 4. Launch Browser
timeout /t 8
start chrome http://localhost:5173
