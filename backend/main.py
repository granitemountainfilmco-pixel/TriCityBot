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
    # PHONETIC SCRUBBER: Hard-coded fixes for common voice-to-text mistakes
    user_input = query.text.lower().replace("or tx", "rtx").replace("forty ninety", "4090").replace("fifty ninety", "5090")
    print(f"Sanitized Input: {user_input}")
    
    inv_keys = ['add', 'remove', 'delete', 'check', 'stock', 'inventory', 'have']
    
    try:
        if any(k in user_input for k in inv_keys):
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': 'Extractor: If product and price are merged like "rtx50902500", split into Name="RTX 5090", Price=2500.'},
                    {'role': 'user', 'content': user_input}
                ],
                tools=[tools.add_to_inventory, tools.check_inventory, tools.remove_from_inventory]
            )
            if response.message.tool_calls:
                res = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
                return {"response": " ".join(res)}
            return {"response": response.message.content}
        else:
            kw = ollama.generate(model='llama3.1', prompt=f"Search keywords: '{user_input}'")['response'].strip()
            data = tools.web_research(kw)
            summary = ollama.chat(model='llama3.1', messages=[{'role': 'system', 'content': 'Summarize research in one sentence.'}, {'role': 'user', 'content': f"Data: {data}\nQ: {user_input}"}])
            return {"response": summary.message.content}
    except Exception as e:
        return {"response": f"System Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
