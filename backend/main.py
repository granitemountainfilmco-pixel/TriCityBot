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
    user_input = query.text.lower()
    
    # 1. Clean phonetic errors before AI sees them
    user_input = user_input.replace("or tx", "rtx").replace("forty ninety", "4090").replace("fifty ninety", "5090")
    
    inv_keys = ['add', 'remove', 'delete', 'check', 'stock', 'inventory', 'have']
    
    try:
        if any(k in user_input for k in inv_keys):
            # Pass 1: Extraction & Standardization
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {
                        'role': 'system', 
                        'content': 'You are a precise data extractor. Split messy input into "name" and "price". '
                                   'If input is "rtx50902500", Name is "RTX 5090", Price is 2500. '
                                   'Remove words like "add", "at", or "for" from the product name.'
                    },
                    {'role': 'user', 'content': user_input}
                ],
                tools=[tools.add_to_inventory, tools.check_inventory, tools.remove_from_inventory]
            )
            
            if response.message.tool_calls:
                res_list = []
                for t in response.message.tool_calls:
                    func = getattr(tools, t.function.name)
                    res_list.append(func(**t.function.arguments))
                return {"response": " ".join(res_list)}
            
            return {"response": response.message.content}
        
        else:
            # Research Path (Unchanged but refined)
            kw = ollama.generate(model='llama3.1', prompt=f"Search keywords for: '{user_input}'")['response'].strip()
            data = tools.web_research(kw)
            summary = ollama.chat(model='llama3.1', messages=[{'role': 'system', 'content': 'Summarize research in one short sentence.'}, {'role': 'user', 'content': f"Data: {data}\nQ: {user_input}"}])
            return {"response": summary.message.content}
            
    except Exception as e:
        return {"response": f"System error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
