#!/bin/bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 1. Ollama
ollama serve &

# 2. Backend (Runs in background terminal)
cd "$ROOT_DIR/backend"
source venv/bin/activate
pip install -r requirements.txt --quiet
gnome-terminal --title="ShopOS-Backend" -- bash -c "cd '$ROOT_DIR/backend'; source venv/bin/activate; python3 main.py; exec bash" &

# 3. Frontend (Runs in background terminal)
cd "$ROOT_DIR/frontend"
npm install
gnome-terminal --title="ShopOS-Frontend" -- bash -c "cd '$ROOT_DIR/frontend'; npm run dev -- --force; exec bash" &

# 4. Launch Browser
sleep 8
xdg-open http://localhost:5173
