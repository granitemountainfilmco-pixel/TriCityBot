import re
import uvicorn
import ollama
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tools # Import the whole module to access functions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# REQUEST MODEL (Matches Frontend)
# =========================
class ChatRequest(BaseModel):
    text: str # Changed from 'message' to 'text' to fix 422 error

# =========================
# COMMAND ROUTER
# =========================
def route_command(user_input: str):
    user_input = user_input.lower().strip()

    # 1. ROBUST ADD LOGIC (Handles names with numbers like RTX 5090)
    # Matches: "add [name] [price]", "add [name] at [price]", etc.
    add_match = re.search(r"add\s+(.*?)\s+(?:for|at|is)?\s*[\$\s]*(\d+(?:\.\d{2})?)(?:\s+(?:qty|x)?\s*(\d+))?$", user_input)
    if add_match:
        name, price, qty = add_match.groups()
        qty = int(qty) if qty else 1
        return tools.add_to_inventory(name, price, qty)

    # 2. INVENTORY MANAGEMENT (Check/Remove/List)
    if any(k in user_input for k in ["check", "stock", "have"]):
        # Use AI to find the item name in the sentence
        response = ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': user_input}], 
                               tools=[{'type': 'function', 'function': {'name': 'check_inventory', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}}}} }])
        if response.message.tool_calls:
            return tools.check_inventory(**response.message.tool_calls[0].function.arguments)

    if "list" in user_input:
        return tools.list_inventory()

    if "remove" in user_input or "delete" in user_input:
        name = user_input.replace("remove", "").replace("delete", "").strip()
        return tools.remove_from_inventory(name)

    # 3. RESEARCH (Uses AI to extract keywords first to avoid 'AdGuard' noise)
    if "research" in user_input or "find" in user_input:
        # Extract just the product name from the request
        kw_gen = ollama.generate(model='llama3.1', prompt=f"Extract only the product name from: '{user_input}'. Output only the name.")
        query = kw_gen['response'].strip()
        print(f"DEBUG: Searching web for: {query}")
        return tools.web_research(query)

    return "I understood the wake word, but I'm not sure what you want to do. Try 'add RTX 5090 2500'."

# =========================
# API ENDPOINT
# =========================
@app.post("/api/chat")
async def chat(req: ChatRequest):
    # Wake word filter
    msg = req.text.lower().strip()
    trigger_words = ["hey shop", "okay shop", "shop"]
    
    remainder = None
    for w in trigger_words:
        if msg.startswith(w):
            remainder = msg[len(w):].strip()
            break
            
    if not remainder:
        return {"response": None}

    response = route_command(remainder)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
