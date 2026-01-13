@echo off
echo Starting ShopOS Ecosystem...

:: 1. Start Ollama in the background
start /min ollama serve

:: 2. Start Backend
echo Launching Backend...
start "ShopOS-Backend" cmd /k "cd backend && venv\Scripts\activate && python main.py"

:: 3. Start Frontend
echo Launching Frontend...
start "ShopOS-Frontend" cmd /k "cd frontend && npm run dev"

:: 4. Wait a moment for servers to initialize, then open Chrome
timeout /t 5
start chrome http://localhost:5173
