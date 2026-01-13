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
    
    # 1. Phonetic Correction
    user_input = user_input.replace("or tx", "rtx").replace("fifty ninety", "5090")

    # 2. Hard Regex for "Add" (Stops AI Monologue)
    # Catches: "add rtx 5090-2500" or "add a6000 4000"
    add_match = re.search(r"add\s+(.+?)[\s-]*(\d+)", user_input)
    if add_match:
        name, price = add_match.groups()
        return {"response": tools.add_to_inventory(name, price)}

    inv_keys = ['check', 'stock', 'inventory', 'remove', 'delete']
    
    try:
        if any(k in user_input for k in inv_keys):
            # Database tool calling
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': "Silent Tool. ONLY call functions. No talk."},
                    {'role': 'user', 'content': user_input}
                ],
                tools=[tools.check_inventory, tools.remove_from_inventory]
            )
            if response.message.tool_calls:
                res = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
                return {"response": " ".join(res)}
            return {"response": response.message.content}

        else:
            # 3. RESEARCH PATH (RAG)
            # Fetch 2 keywords for search
            kw_gen = ollama.generate(model='llama3.1', prompt=f"Keywords for: '{user_input}'. Output ONLY words.")
            web_data = tools.web_research(kw_gen['response'].strip())
            
            # Injection: The AI is FORCED to use this text
            summary = ollama.chat(
                model='llama3.1',
                messages=[
                    {
                        'role': 'system', 
                        'content': f"DATA SOURCE (TRUST THIS): \n{web_data}\n\n"
                                   "RULE: Use ONLY the data above. If price is missing, say so. "
                                   "Do NOT mention RTX 3090 unless it is in the data."
                    },
                    {'role': 'user', 'content': f"Explain {user_input}."}
                ]
            )
            return {"response": summary.message.content}
            
    except Exception as e:
        return {"response": "I'm having trouble processing that right now."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
