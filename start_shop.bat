@echo off
set "ROOT_DIR=%~dp0"

:: 1. Start Ollama
start /min "" ollama serve

:: 2. Backend
cd /d "%ROOT_DIR%backend"
call venv\Scripts\activate
start "ShopOS-Backend" cmd /k "python main.py"

:: 3. Frontend
cd /d "%ROOT_DIR%frontend"
:: Force Vite to ignore old cache and use the new App.tsx paths
start "ShopOS-Frontend" cmd /k "npm run dev -- --force"

:: 4. Launch
timeout /t 5
start chrome http://localhost:5173
