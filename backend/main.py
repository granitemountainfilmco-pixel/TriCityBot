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

@app.post("/api/chat")
async def chat(query: Query):
    user_input = query.text.strip().lower()
    
    # --- VOICE TRIGGER ---
    trigger_words = ["hey shop", "assistant", "okay shop", "shop"]
    if not any(user_input.startswith(word) for word in trigger_words) and len(user_input.split()) > 1:
        return {"response": ""} 

    # --- 1. THE DATA EXTRACTOR (Fixes "5090500") ---
    # This captures everything after 'add' until the last number group
    add_match = re.search(r"add\s+(.+?)\s*(?:for|at|[:\-])?\s*\$?(\d+)$", user_input)
    if add_match:
        name, price = add_match.groups()
        return {"response": tools.add_to_inventory(name, price)}

    # --- 2. INVENTORY CHECK ---
    if any(k in user_input for k in ['check', 'stock', 'inventory', 'have']):
        response = ollama.chat(
            model='llama3.1',
            messages=[{'role': 'system', 'content': "Output ONLY tool calls."}, {'role': 'user', 'content': user_input}],
            tools=[tools.check_inventory, tools.remove_from_inventory]
        )
        if response.message.tool_calls:
            res = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
            return {"response": " ".join(res)}

    # --- 3. THE RESEARCH PATH (Strict One-Sentence Fix) ---
    kw_gen = ollama.generate(model='llama3.1', prompt=f"Keywords for: '{user_input}'. Words only.")
    web_data = tools.web_research(kw_gen['response'].strip())
    
    summary = ollama.chat(
        model='llama3.1',
        messages=[{
            'role': 'system', 
            'content': f"FACTS: {web_data}\n\nINSTRUCTION: Answer in ONE short sentence (max 15 words). No intro."
        }, {'role': 'user', 'content': user_input}]
    )
    return {"response": summary.message.content}

if __name__ == "__main__":
    import uvicorn
    # This starts the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
