#!/bin/bash

# Get the absolute path to the script location
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Root directory: $ROOT_DIR"

# 1. Start Ollama in the background
if ! pgrep -x "ollama" > /dev/null
then
    echo "Starting Ollama..."
    ollama serve &
fi

# 2. Setup & Launch Backend
echo "Setting up Backend..."
cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet

# Launch Backend in a new terminal
gnome-terminal --title="ShopOS-Backend" -- bash -c "cd '$ROOT_DIR/backend' && source venv/bin/activate && python3 main.py; exec bash"

# 3. Setup & Launch Frontend
echo "Setting up Frontend..."
cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install
fi

# Launch Frontend with --force to clear the Vite cache issue
gnome-terminal --title="ShopOS-Frontend" -- bash -c "cd '$ROOT_DIR/frontend' && npm run dev -- --force; exec bash"

# 4. Launch Browser
echo "Waiting for servers to warm up..."
sleep 8
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5173
elif command -v google-chrome > /dev/null; then
    google-chrome http://localhost:5173
fi
