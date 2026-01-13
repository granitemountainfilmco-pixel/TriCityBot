#!/bin/bash

# Find the current directory
ROOT_DIR=$(pwd)
echo "Root directory: $ROOT_DIR"

# 1. Start Ollama
ollama serve & 

# 2. Setup Backend
echo "Setting up Backend..."
cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
gnome-terminal --title="ShopOS-Backend" -- bash -c "cd $ROOT_DIR/backend && source venv/bin/activate && python3 main.py; exec bash"

# 3. Setup Frontend
echo "Setting up Frontend..."
cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install
fi
gnome-terminal --title="ShopOS-Frontend" -- bash -c "cd $ROOT_DIR/frontend && npm run dev; exec bash"

# 4. Launch Browser
sleep 8
xdg-open http://localhost:5173
