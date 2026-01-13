@echo off
set "ROOT_DIR=%~dp0"

:: 1. Backend
cd /d "%ROOT_DIR%backend"
call venv\Scripts\activate
start "ShopOS-Backend" cmd /k "venv\Scripts\activate && python main.py"

:: 2. Frontend (The Root Fix)
cd /d "%ROOT_DIR%frontend"
:: Clean the cache to fix the blank screen issue
if exist "node_modules\.vite" rmdir /s /q "node_modules\.vite"
start "ShopOS-Frontend" cmd /k "npm run dev -- --force"

:: 3. Launch
timeout /t 8
start chrome http://localhost:5173
