@echo off
set "ROOT_DIR=%~dp0"

:: 1. Force Reset Ollama
echo [OLLAMA] Cleaning up background processes...
taskkill /f /im ollama.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: 2. Start Ollama Server (Visible for Debugging)
echo [OLLAMA] Starting Server...
start "OLLAMA-SERVER" cmd /c "ollama serve"
timeout /t 5 /nobreak

:: 3. Ensure Model Exists (Prevents backend hanging)
echo [OLLAMA] Verifying llama3.1...
ollama pull llama3.1

:: 4. Backend Setup
echo [BACKEND] Starting...
cd /d "%ROOT_DIR%backend"
if not exist "venv" (
    python -m venv venv
)
start "ShopOS-Backend" cmd /k "call venv\Scripts\activate && pip install -r requirements.txt --quiet && python main.py"

:: 5. Frontend Setup
echo [FRONTEND] Starting...
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" (
    call npm install
)
start "ShopOS-Frontend" cmd /k "npm run dev -- --force"

:: 6. Launch Browser
timeout /t 4
start chrome http://localhost:5173
