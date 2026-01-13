#!/bin/bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 1. Backend
cd "$ROOT_DIR/backend"
[ ! -d "venv" ] && python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --quiet
gnome-terminal --title="ShopOS-Backend" -- bash -c "source venv/bin/activate; python3 main.py; exec bash" &

# 2. Frontend
cd "$ROOT_DIR/frontend"
[ ! -d "node_modules" ] && npm install
gnome-terminal --title="ShopOS-Frontend" -- bash -c "npm run dev -- --force; exec bash" &

# 3. Launch
sleep 8
xdg-open http://localhost:5173
