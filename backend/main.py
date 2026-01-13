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
    user_input = query.text.lower().strip()
    
    # 1. HARD-CODED EXTRACTION (Anti-Hallucination Layer)
    # If user says "add name-price", bypass the AI's "monologue" entirely
    add_match = re.match(r"add\s+(.+)-(\d+)", user_input)
    if add_match:
        name, price = add_match.groups()
        return {"response": tools.add_to_inventory(name, price)}

    inv_keys = ['add', 'remove', 'delete', 'check', 'stock', 'inventory', 'have']
    
    try:
        if any(k in user_input for k in inv_keys):
            # 2. SILENT SYSTEM PROMPT
            # This stops the "JSON-style" inner monologue
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {
                        'role': 'system', 
                        'content': "You are a silent shop database tool. "
                                   "ONLY respond with a tool call. "
                                   "DO NOT explain. DO NOT use 'split_string' or 'extract_price'. "
                                   "Use ONLY: add_to_inventory, check_inventory, or remove_from_inventory."
                    },
                    {'role': 'user', 'content': user_input}
                ],
                tools=[tools.add_to_inventory, tools.check_inventory, tools.remove_from_inventory]
            )
            
            if response.message.tool_calls:
                res = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
                return {"response": " ".join(res)}
            return {"response": response.message.content}

        else:
            # 3. RESEARCH PATH (RAG Pattern)
            kw_gen = ollama.generate(model='llama3.1', prompt=f"2 words for: '{user_input}'. Output ONLY words.")
            web_data = tools.web_research(kw_gen['response'].strip())
            
            summary = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': f"Use ONLY this data: {web_data}"},
                    {'role': 'user', 'content': f"Summarize info for: {user_input}"}
                ]
            )
            return {"response": summary.message.content}
    except Exception as e:
        return {"response": "System busy. Try again."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
