#!/bin/bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 1. Start Ollama (Ubuntu standard)
if systemctl is-active --quiet ollama; then
    echo "[OLLAMA] Service already running."
else
    echo "[OLLAMA] Starting service..."
    ollama serve &
    sleep 5
fi

# 2. Ensure Model
ollama pull llama3.1

# 3. Backend Setup
cd "$ROOT_DIR/backend"
[ ! -d "venv" ] && python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --quiet
gnome-terminal --title="ShopOS-Backend" -- bash -c "source venv/bin/activate; python3 main.py; exec bash" &

# 4. Frontend Setup
cd "$ROOT_DIR/frontend"
[ ! -d "node_modules" ] && npm install
gnome-terminal --title="ShopOS-Frontend" -- bash -c "npm run dev -- --force; exec bash" &

# 5. Launch
sleep 10
xdg-open http://localhost:5173
