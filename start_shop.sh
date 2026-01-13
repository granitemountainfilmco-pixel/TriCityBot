#!/bin/bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 1. Ollama
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &
fi

# 2. Backend
echo "[BACKEND] Preparing..."
cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "[BACKEND] Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt --quiet
# Launch in background terminal
gnome-terminal --title="ShopOS-Backend" -- bash -c "cd '$ROOT_DIR/backend' && source venv/bin/activate && python3 main.py; exec bash"

# 3. Frontend
echo "[FRONTEND] Preparing..."
cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install
fi
# Launch in background terminal
gnome-terminal --title="ShopOS-Frontend" -- bash -c "cd '$ROOT_DIR/frontend' && npm run dev -- --force; exec bash"

# 4. Open browser
sleep 8
xdg-open http://localhost:5173 || google-chrome http://localhost:5173
