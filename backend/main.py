import re
import uvicorn
import ollama
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tools 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CONFIG & MODELS
# =========================
WAKE_WORDS = ["hey shop", "okay shop", "shop"]

class ChatRequest(BaseModel):
    text: str # Fixed: Matches the 'text' key sent by your frontend

# =========================
# COMMAND ROUTER
# =========================
def route_command(user_input: str):
    user_input = user_input.lower().strip()

    # 1. ROBUST ADD (Greedy Regex)
    # This (.*) captures "RTX 5090" correctly because it looks for the LAST number for the price.
    add_match = re.search(r"add\s+(.*)\s+(?:for|at|is)?\s*[\$\s]*(\d+(?:\.\d{2})?)(?:\s+(?:qty|x)?\s*(\d+))?$", user_input)
    if add_match:
        name, price, qty = add_match.groups()
        qty = int(qty) if qty else 1
        return tools.add_to_inventory(name, price, qty)

    # 2. INVENTORY (Check/List/Remove)
    if any(k in user_input for k in ["check", "stock", "have"]):
        # Extract item name using AI for flexibility
        kw = ollama.generate(model='llama3.1', prompt=f"What product is being asked about in: '{user_input}'? Output ONLY the name.")
        return tools.check_inventory(kw['response'].strip())

    if "list" in user_input:
        return tools.list_inventory()

    if "remove" in user_input or "delete" in user_input:
        name = user_input.replace("remove", "").replace("delete", "").strip()
        return tools.remove_from_inventory(name)

    # 3. RESEARCH (Limited to 3 Sentences)
    if "research" in user_input or "find" in user_input:
        # Extract topic to prevent "hey shop" noise in search
        topic_gen = ollama.generate(model='llama3.1', prompt=f"Extract only the product name from: '{user_input}'.")
        query = topic_gen['response'].strip()
        
        web_data = tools.web_research(query)
        
        # Enforce the 3-sentence limit in the system prompt
        summary = ollama.chat(
            model='llama3.1',
            messages=[{
                'role': 'system', 
                'content': f"FACTS: {web_data}\n\nINSTRUCTION: Summarize these facts in EXACTLY 3 sentences. Be objective and brief."
            }, {'role': 'user', 'content': f"Research details for {query}"}]
        )
        return summary.message.content

    return "I'm not sure how to help with that. Try 'add RTX 5090 2500'."

# =========================
# API ENDPOINT
# =========================
@app.post("/api/chat")
async def chat(req: ChatRequest):
    msg = req.text.lower().strip()
    
    # Filter for Wake Word
    remainder = None
    for w in WAKE_WORDS:
        if msg.startswith(w):
            remainder = msg[len(w):].strip()
            break
            
    if not remainder:
        return {"response": None}

    response = route_command(remainder)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
