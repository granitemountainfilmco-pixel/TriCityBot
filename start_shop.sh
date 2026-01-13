#!/bin/bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 1. Force Reset & Start Ollama
echo "[OLLAMA] Ensuring server is active..."
# On Linux, Ollama usually runs as a systemd service. 
# We'll try to start it if it's not active.
if ! systemctl is-active --quiet ollama; then
    echo "[OLLAMA] Starting service via systemctl..."
    sudo systemctl start ollama
fi

# 2. Wait for API to respond
echo "[OLLAMA] Waiting for API on port 11434..."
until curl -s http://localhost:11434 > /dev/null; do
  sleep 1
done

# 3. Ensure Model is loaded
echo "[OLLAMA] Pulling llama3.1 (checking for updates)..."
ollama pull llama3.1

# 4. Launch Backend & Frontend
cd "$ROOT_DIR/backend"
source venv/bin/activate
pip install -r requirements.txt --quiet
gnome-terminal --title="ShopOS-Backend" -- bash -c "source venv/bin/activate; python3 main.py; exec bash" &

cd "$ROOT_DIR/frontend"
gnome-terminal --title="ShopOS-Frontend" -- bash -c "npm run dev -- --host; exec bash" &

echo "ShopOS is ready!"
xdg-open http://localhost:5173
