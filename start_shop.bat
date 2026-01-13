@echo off
set "ROOT_DIR=%~dp0"

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    set /p conf="Python missing. Install via Winget? (y/n): "
    if /i "%conf%"=="y" winget install -e --id Python.Python.3.11
)

:: 2. Check Node
node -v >nul 2>&1
if %errorlevel% neq 0 (
    set /p conf="Node.js missing. Install via Winget? (y/n): "
    if /i "%conf%"=="y" winget install -e --id OpenJS.NodeJS
)

:: 3. Check Ollama
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    set /p conf="Ollama missing. Install? (y/n): "
    if /i "%conf%"=="y" winget install -e --id Ollama.Ollama
)

:: 4. Backend
cd /d "%ROOT_DIR%backend"
if not exist "venv" ( python -m venv venv )
start "Backend" cmd /k "call venv\Scripts\activate && pip install -r requirements.txt && python main.py"

:: 5. Frontend
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" ( call npm install )
start "Frontend" cmd /k "npm run dev -- --force"

timeout /t 5
start chrome http://localhost:5173
