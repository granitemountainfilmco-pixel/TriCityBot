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
    
    # 1. TRIGGER WORD CLEANUP
    trigger_words = ["hey shop", "assistant", "okay shop", "shop"]
    is_triggered = any(word in user_input for word in trigger_words)
    if not is_triggered: return {"response": ""}

    # 2. DATA EXTRACTOR (Fixes "5090500")
    add_match = re.search(r"add\s+(.+?)\s*(?:for|at|[:\-])?\s*(\d+)$", user_input)
    if add_match:
        name, price = add_match.groups()
        return {"response": tools.add_to_inventory(name, price)}

    # 3. INVENTORY CHECK (Restored Logic)
    if any(k in user_input for k in ['check', 'stock', 'inventory']):
        response = ollama.chat(
            model='llama3.1',
            messages=[{'role': 'system', 'content': "Output ONLY tool calls."}, {'role': 'user', 'content': user_input}],
            tools=[tools.check_inventory, tools.remove_from_inventory]
        )
        if response.message.tool_calls:
            res = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
            return {"response": " ".join(res)}

    # 4. RESEARCH PATH (Concise)
    kw_gen = ollama.generate(model='llama3.1', prompt=f"Keywords for: '{user_input}'.")
    web_data = tools.web_research(kw_gen['response'].strip())
    summary = ollama.chat(
        model='llama3.1',
        messages=[
            {'role': 'system', 'content': f"FACTS: {web_data}\n\nINSTRUCTION: Answer in ONE sentence (max 15 words)."},
            {'role': 'user', 'content': user_input}
        ]
    )
    return {"response": summary.message.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
