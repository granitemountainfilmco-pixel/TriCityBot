#!/bin/bash
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$ROOT_DIR"

install_component() {
    read -p "$1 is missing. Would you like to install it? (y/n): " confirm
    if [[ $confirm == [yY] ]]; then
        return 0
    else
        return 1
    fi
}

# 1. Check/Install Docker
if ! command -v docker &> /dev/null; then
    if install_component "Docker"; then
        echo "[INSTALL] Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        echo "Please log out and log back in for Docker permissions to take effect."
    else
        exit 1
    fi
fi

# 2. Check/Install Ollama
if ! command -v ollama &> /dev/null; then
    if install_component "Ollama"; then
        echo "[INSTALL] Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
fi

# 3. Fire up the containers
echo "[DOCKER] Building and starting ShopOS..."
docker compose up --build -d

# 4. Launch
echo "Waiting for services..."
sleep 5
xdg-open http://localhost:5173
