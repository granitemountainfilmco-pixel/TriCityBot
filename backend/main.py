import re
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tools import (
    add_to_inventory,
    remove_from_inventory,
    check_inventory,
    list_inventory,
    web_research
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CONFIG
# =========================

WAKE_WORDS = ["hey shop"]
VALID_COMMANDS = {"add", "remove", "check", "list", "research"}

# =========================
# REQUEST MODEL
# =========================

class ChatRequest(BaseModel):
    message: str

# =========================
# HELPERS
# =========================

def extract_after_wake(message: str):
    msg = message.lower().strip()
    for w in WAKE_WORDS:
        if msg.startswith(w):
            return msg[len(w):].strip()
    return None


def parse_add_args(args):
    price = None
    price_index = None

    for i in reversed(range(len(args))):
        token = args[i].replace(".", "", 1)
        if token.isdigit():
            price = float(args[i])
            price_index = i
            break

    if price is None or price_index == 0:
        return None

    name = " ".join(args[:price_index])
    qty = 1

    if price_index + 1 < len(args) and args[price_index + 1].isdigit():
        qty = int(args[price_index + 1])

    return name, price, qty

# =========================
# COMMAND ROUTER
# =========================

def route_command(text: str):
    parts = text.split()
    if not parts:
        return None

    cmd = parts[0]
    args = parts[1:]

    if cmd not in VALID_COMMANDS:
        return None

    if cmd == "add":
        parsed = parse_add_args(args)
        if not parsed:
            return "Usage: hey shop add <item> <price> [qty]"
        name, price, qty = parsed
        add_to_inventory(name, price, qty)
        return f"Successfully logged: {name} at ${price:.2f} (x{qty})."

    if cmd == "remove":
        if not args:
            return "Usage: hey shop remove <item>"
        name = " ".join(args)
        remove_from_inventory(name)
        return f"Removed {name} from inventory."

    if cmd == "check":
        if not args:
            return "Usage: hey shop check <item>"
        return check_inventory(" ".join(args))

    if cmd == "list":
        return list_inventory()

    if cmd == "research":
        if not args:
            return "Usage: hey shop research <query>"
        return web_research(" ".join(args))

# =========================
# API ENDPOINT
# =========================

@app.post("/api/chat")
async def chat(req: ChatRequest):
    remainder = extract_after_wake(req.message)
    if remainder is None or not remainder:
        return {"response": None}

    response = route_command(remainder)
    return {"response": response}

# =========================
# ENTRY POINT (THIS WAS MISSING)
# =========================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
