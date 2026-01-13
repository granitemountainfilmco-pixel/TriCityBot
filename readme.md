README.md

ShopOS: Computer Shop Management System

Prerequisites

    Ollama: Download and run ollama pull llama3.1

    Python 3.10+

    Node.js & npm

1. Brain (Ollama) Run in terminal: ollama serve

2. Backend (FastAPI) Run in new terminal:
Bash

cd backend
python3 -m venv venv
# Windows
venv\Scripts\activate
# Ubuntu/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

3. Frontend (React) Run in new terminal:
Bash

cd frontend
npm install
npm run dev

Access at http://localhost:5173

Features

    Add: "Add to inventory [item], price [number], notes [text]"

    Remove: "Remove from inventory [item]"

    Check: "Check inventory for [item]"

    Research: "Research [topic]" (Uses DuckDuckGo)

File Structure

    /backend: Python logic and SQLite database.

    /frontend: React/TypeScript interface.
