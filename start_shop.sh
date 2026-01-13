#!/bin/bash

echo "Starting ShopOS Ecosystem..."

# 1. Ensure Ollama is running
ollama serve & 

# 2. Start Backend in a new terminal tab/window
gnome-terminal --title="ShopOS-Backend" -- bash -c "cd backend && source venv/bin/activate && python3 main.py; exec bash"

# 3. Start Frontend in a new terminal tab/window
gnome-terminal --title="ShopOS-Frontend" -- bash -c "cd frontend && npm run dev; exec bash"

# 4. Wait and open Chrome/Firefox
sleep 5
xdg-open http://localhost:5173
