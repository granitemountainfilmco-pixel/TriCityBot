#!/bin/bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to check and install dependencies
check_install() {
    if ! command -v $1 &> /dev/null; then
        read -p "$1 is missing. Install it? (y/n): " confirm
        if [[ $confirm == [yY] ]]; then
            sudo apt update
            sudo apt install -y $2
        else
            echo "Cannot continue without $1."
            exit 1
        fi
    fi
}

# 1. Install System Basics
check_install "python3" "python3 python3-venv python3-pip"
check_install "node" "nodejs npm"
check_install "curl" "curl"

# 2. Check/Install Ollama
if ! command -v ollama &> /dev/null; then
    read -p "Ollama missing. Install it? (y/n): " confirm
    if [[ $confirm == [yY] ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
    fi
fi

# 3. Setup Backend
echo "[BACKEND] Preparing environment..."
cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then python3 -m venv venv; fi
source venv/bin/activate
pip install -r requirements.txt --quiet
gnome-terminal --title="ShopOS-Backend" -- bash -c "source venv/bin/activate; python3 main.py; exec bash" &

# 4. Setup Frontend
echo "[FRONTEND] Preparing Node modules..."
cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then npm install; fi
gnome-terminal --title="ShopOS-Frontend" -- bash -c "npm run dev -- --force; exec bash" &

echo "Launching ShopOS..."
sleep 8
xdg-open http://localhost:5173
