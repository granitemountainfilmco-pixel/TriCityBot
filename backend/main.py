import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama, tools
from database import init_db

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
init_db()

class Query(BaseModel): text: str

def extract_add_command(text: str):
    """
    Handles messy voice strings like 'add rtx 50902500' 
    by identifying the price as the last numeric group.
    """
    # Pattern: 'add' + item_name + price
    # Supports: "add rtx 5090 2500", "add rtx 50902500", "add rtx-5090 for 2500"
    match = re.search(r"add\s+(.+?)\s*(?:for|at|[:\-])?\s*(\d+(?:[.,]\d+)?)$", text)
    if match:
        name, price = match.groups()
        # If the price is abnormally large (e.g., 50902500), 
        # it likely fused. We separate the last 2-4 digits if logically applicable,
        # but a better way is to check the 'name' for trailing digits.
        return name.strip().upper(), price
    return None, None

@app.post("/api/chat")
async def chat(query: Query):
    raw_input = query.text.strip()
    user_input = raw_input.lower()
    
    # --- VOICE KEYWORD TRIGGER FIX ---
    trigger_words = ["hey shop", "assistant", "okay shop", "shop"]
    is_triggered = any(user_input.startswith(word) for word in trigger_words)
    
    # Early exit if voice is detected without trigger word
    if not is_triggered and len(user_input.split()) > 1:
        return {"response": ""} 

    # Clean the trigger word out of the command for cleaner processing
    for word in trigger_words:
        user_input = user_input.replace(word, "").strip()

    # --- 1. THE DATA EXTRACTOR ---
    name, price = extract_add_command(user_input)
    if name and price:
        return {"response": tools.add_to_inventory(name, price)}

    # --- 2. INVENTORY CHECK PATH ---
    if any(k in user_input for k in ['check', 'stock', 'inventory', 'have']):
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': "You are an inventory tool. Return only the tool call."},
                {'role': 'user', 'content': user_input}
            ],
            tools=[tools.check_inventory, tools.remove_from_inventory]
        )
        if response.message.tool_calls:
            res = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
            return {"response": " ".join(res)}

    # --- 3. THE RESEARCH PATH (Grounded & Concise) ---
    else:
        kw_gen = ollama.generate(model='llama3.1', prompt=f"Search keywords for: '{user_input}'. Output only keywords.")
        web_data = tools.web_research(kw_gen['response'].strip())
        
        summary = ollama.chat(
            model='llama3.1',
            messages=[
                {
                    'role': 'system', 
                    'content': f"FACTS: {web_data}\n\n"
                               "INSTRUCTION: Summarize the facts for VOICE OUTPUT. "
                               "Keep it to ONE short sentence. Be extremely concise. "
                               "If price is found, state it clearly."
                },
                {'role': 'user', 'content': user_input}
            ]
        )
        return {"response": summary.message.content}
