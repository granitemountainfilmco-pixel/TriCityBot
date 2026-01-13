@echo off
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

:: 1. Check for Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    set /p confirm="Docker not found. Install Docker Desktop via Winget? (y/n): "
    if /i "%confirm%"=="y" (
        echo [INSTALL] Installing Docker Desktop...
        winget install -e --id Docker.DockerDesktop
        echo Please restart your computer after installation completes.
        pause
        exit /b
    ) else (
        exit /b
    )
)

:: 2. Check for Ollama
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    set /p confirm="Ollama not found. Install Ollama? (y/n): "
    if /i "%confirm%"=="y" (
        echo [INSTALL] Downloading Ollama...
        winget install -e --id Ollama.Ollama
    )
)

:: 3. Build and Start
echo [DOCKER] Starting ShopOS Containers...
docker compose up --build -d

:: 4. Launch Browser
timeout /t 5
start chrome http://localhost:5173
pause
