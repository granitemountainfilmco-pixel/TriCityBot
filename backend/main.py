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

def extract_add_parts(text: str):
    """
    Solves the '5090500' issue by splitting the last numeric group 
    from the product name.
    """
    # Regex looks for 'add', then the name, then the final number group
    match = re.search(r"add\s+(.+?)\s*(?:for|at|[:\-])?\s*\$?(\d+(?:[.,]\d+)?)$", text)
    if match:
        name, price = match.groups()
        return name.strip().upper(), price
    return None, None

@app.post("/api/chat")
async def chat(query: Query):
    raw_input = query.text.strip()
    user_input = raw_input.lower()
    
    # --- TRIGGER LOGIC ---
    trigger_words = ["hey shop", "assistant", "okay shop", "shop"]
    is_triggered = any(user_input.startswith(word) for word in trigger_words)
    
    # Exit if no trigger word found in voice input
    if not is_triggered and len(user_input.split()) > 1:
        return {"response": ""} 

    # Strip trigger word so it doesn't mess up search keywords
    for word in trigger_words:
        user_input = user_input.replace(word, "").strip()

    # --- 1. THE DATA EXTRACTOR ---
    name, price = extract_add_parts(user_input)
    if name and price:
        return {"response": tools.add_to_inventory(name, price)}

    # --- 2. INVENTORY CHECK PATH ---
    if any(k in user_input for k in ['check', 'stock', 'inventory', 'have']):
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': "Tool mode. Return ONLY the tool call."},
                {'role': 'user', 'content': user_input}
            ],
            tools=[tools.check_inventory, tools.remove_from_inventory]
        )
        if response.message.tool_calls:
            res = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
            return {"response": " ".join(res)}

    # --- 3. THE RESEARCH PATH (Strictly Concise) ---
    else:
        # Step A: Minimal keywords
        kw_gen = ollama.generate(model='llama3.1', prompt=f"Search keywords for: '{user_input}'. Keywords only.")
        web_data = tools.web_research(kw_gen['response'].strip())
        
        # Step B: Strict Grounding
        summary = ollama.chat(
            model='llama3.1',
            messages=[
                {
                    'role': 'system', 
                    'content': (
                        f"FACTS: {web_data}\n"
                        "INSTRUCTIONS: Answer the user using ONLY the facts. "
                        "You must be BRIEF. Use ONE short sentence only if possible, more if necesssary for a detailed question. "
                        "Do not say 'Based on the facts' or 'According to the web'."
                    )
                },
                {'role': 'user', 'content': user_input}
            ]
        )
        return {"response": summary.message.content}
