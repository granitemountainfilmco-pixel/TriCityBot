import re
import uvicorn
import ollama
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tools 

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELS (Matches Frontend)
# =========================
class ChatRequest(BaseModel):
    text: str  # Must be 'text' to match ChatInterface.tsx

# =========================
# COMMAND ROUTER
# =========================
def route_command(user_input: str):
    user_input = user_input.lower().strip()

    # 1. ADD LOGIC (Greedy Regex)
    # This captures everything for the name until it finds the LAST number in the string.
    add_pattern = r"add\s+(.*)\s+(?:for|at|is)?\s*[\$\s]*(\d+(?:\.\d{2})?)(?:\s+(?:qty|x)?\s*(\d+))?$"
    add_match = re.search(add_pattern, user_input)
    
    if add_match:
        name, price, qty = add_match.groups()
        qty = int(qty) if qty else 1
        return tools.add_to_inventory(name, price, qty)

    # 2. INVENTORY MANAGEMENT
    if any(k in user_input for k in ["check", "stock", "have"]):
        # Extract item name using AI to handle "Do we have any RTX 5090s?"
        kw = ollama.generate(model='llama3.1', prompt=f"Extract only the product name from: '{user_input}'. Output only the name.")
        return tools.check_inventory(kw['response'].strip())

    if "list" in user_input:
        return tools.list_inventory()

    if "remove" in user_input or "delete" in user_input:
        name = user_input.replace("remove", "").replace("delete", "").strip()
        return tools.remove_from_inventory(name)

    # 3. RESEARCH (Strict 3-Sentence Summary)
    if any(k in user_input for k in ["research", "find", "price"]):
        # Step A: Clean the query so we don't search for "hey shop research"
        topic_gen = ollama.generate(model='llama3.1', prompt=f"Extract only the product name from: '{user_input}'.")
        query = topic_gen['response'].strip()
        
        # Step B: Fetch web data
        web_data = tools.web_research(query)
        
        # Step C: Summarize with One-Shot instruction
        summary = ollama.chat(
            model='llama3.1',
            messages=[{
                'role': 'system', 
                'content': (
                    "Summarize the FACTS into EXACTLY 3 sentences. Do not use lists. "
                    "Example: The product is currently available at major retailers. It features a new architecture. "
                    "Market prices range between $1,200 and $1,500 depending on the model."
                )
            }, {
                'role': 'user', 
                'content': f"FACTS: {web_data}\n\nSummarize for {query}."
            }],
            options={'temperature': 0.1} # Keeps the AI focused and less creative
        )
        return summary.message.content

    return "Command not recognized. Try: 'Hey shop, add RTX 5090 2500'."

# =========================
# API ENDPOINT
# =========================
@app.post("/api/chat")
async def chat(req: ChatRequest):
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
    from database import init_db
    init_db() # Ensures table exists
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
