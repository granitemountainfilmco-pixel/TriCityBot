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
    # Standardize phonetic errors before processing
    user_input = query.text.lower().replace("or tx", "rtx").replace("forty ninety", "4090").replace("fifty ninety", "5090")
    inv_keys = ['add', 'remove', 'delete', 'check', 'stock', 'inventory', 'have']
    
    try:
        if any(k in user_input for k in inv_keys):
            # Database Path
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': 'Extractor: Split merged product/price like "rtx50902500" into Name="RTX 5090", Price=2500.'},
                    {'role': 'user', 'content': user_input}
                ],
                tools=[tools.add_to_inventory, tools.check_inventory, tools.remove_from_inventory]
            )
            if response.message.tool_calls:
                res = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
                return {"response": " ".join(res)}
            return {"response": response.message.content}
        else:
            # Reliable Research Path
            kw_gen = ollama.generate(model='llama3.1', prompt=f"Convert to 2 search keywords: '{user_input}'. Output ONLY keywords.")
            keywords = kw_gen['response'].strip()
            
            web_data = tools.web_research(keywords)
            
            # FORCE AI to use the fetched data as the only source of truth
            summary = ollama.chat(
                model='llama3.1',
                messages=[
                    {
                        'role': 'system', 
                        'content': f"STRICT: Use ONLY the following Web Data to answer. If the data shows a price, the product exists. \nWeb Data: {web_data}"
                    },
                    {'role': 'user', 'content': f"Based on the data, what is the info for {user_input}?"}
                ]
            )
            return {"response": summary.message.content}
    except Exception as e:
        return {"response": "I'm having trouble processing that right now."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
