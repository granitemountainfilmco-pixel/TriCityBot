#!/bin/bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 1. Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "Error: Ollama is not installed. Please install it from ollama.com"
    exit 1
fi

# 2. Start/Verify Ollama Service
if systemctl is-active --quiet ollama; then
    echo "[OLLAMA] Service already running." 
else
    echo "[OLLAMA] Starting service..." 
    ollama serve & 
    sleep 5 
fi

ollama pull llama3.1 

# 3. Backend Setup
cd "$ROOT_DIR/backend" 
if [ ! -d "venv" ]; then
    echo "[BACKEND] Creating Virtual Environment..."
    python3 -m venv venv 
fi

source venv/bin/activate 
# Professional touch: only install if requirements exist
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet 
fi

# Use & to run in background if they don't have gnome-terminal, 
# or keep your gnome-terminal approach if you know they use default Ubuntu.
gnome-terminal --title="ShopOS-Backend" -- bash -c "source venv/bin/activate; python3 main.py; exec bash" & 

# 4. Frontend Setup
cd "$ROOT_DIR/frontend" 
if [ ! -d "node_modules" ]; then
    echo "[FRONTEND] Installing dependencies..."
    npm install 
fi

gnome-terminal --title="ShopOS-Frontend" -- bash -c "npm run dev -- --force; exec bash" & 

# 5. Launch
echo "Waiting for services to spin up..."
sleep 8
xdg-open http://localhost:5173
