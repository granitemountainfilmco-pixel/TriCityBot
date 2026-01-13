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
    
    # 1. FIX: Number Fusing (e.g., "5090500")
    # This greedy regex captures the name and the final number separately.
    add_match = re.search(r"add\s+(.+?)\s*(?:for|at|[:\-])?\s*(\d+)$", user_input)
    if add_match:
        name, price = add_match.groups()
        return {"response": tools.add_to_inventory(name, price)}

    # 2. FIX: Paragraphs (RAG Path)
    # Forced brevity for voice synthesis.
    if any(k in user_input for k in ['check', 'stock', 'inventory']):
        # (Standard inventory check code here...)
        pass
    else:
        kw_gen = ollama.generate(model='llama3.1', prompt=f"Keywords for: '{user_input}'.")
        web_data = tools.web_research(kw_gen['response'].strip())
        summary = ollama.chat(
            model='llama3.1',
            messages=[{
                'role': 'system', 
                'content': f"FACTS: {web_data}\nINSTRUCTION: Answer in ONE sentence (max 15 words). No preamble."
            }, {'role': 'user', 'content': user_input}]
        )
        return {"response": summary.message.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
