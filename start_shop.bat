@echo off
set "ROOT_DIR=%~dp0"

:: 1. Force Reset Ollama
echo [OLLAMA] Cleaning up background processes...
taskkill /f /im ollama.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: 2. Start Ollama Server
echo [OLLAMA] Starting Server...
:: 'start' runs it in a separate window so it stays open
start "OLLAMA-SERVER" cmd /c "ollama serve"

:: 3. Wait for API to be ready (The "Pinger")
echo [OLLAMA] Waiting for port 11434 to wake up...
:wait_loop
curl -s http://localhost:11434 >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 1 >nul
    goto wait_loop
)
echo [OLLAMA] API is online!

:: 4. Verify Model
echo [OLLAMA] Verifying llama3.1...
ollama pull llama3.1

:: 5. Launch Backend
cd /d "%ROOT_DIR%backend"
call venv\Scripts\activate
start "ShopOS-Backend" cmd /k "python main.py"

:: 6. Launch Frontend
cd /d "%ROOT_DIR%frontend"
start "ShopOS-Frontend" cmd /k "npm run dev -- --force"

timeout /t 5
start chrome http://localhost:5173
