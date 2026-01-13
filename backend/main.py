from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import tools
from database import init_db

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    user_input = query.text.lower()
    print(f"Heard: {user_input}")
    
    # 1. Intent Routing
    inventory_keywords = ['add', 'remove', 'delete', 'check', 'inventory', 'stock', 'have']
    
    if any(k in user_input for k in inventory_keywords):
        # LOCAL INVENTORY PATH
        response = ollama.chat(
            model='llama3.1',
            messages=[{'role': 'user', 'content': query.text}],
            tools=[tools.add_to_inventory, tools.check_inventory, tools.remove_from_inventory]
        )
        
        if response.message.tool_calls:
            results = []
            for tool in response.message.tool_calls:
                func = getattr(tools, tool.function.name)
                results.append(func(**tool.function.arguments))
            return {"response": " ".join(results)}
        return {"response": response.message.content}

    else:
        # DEEP RESEARCH PATH
        # Step A: Keyword Clean-up
        kw_gen = ollama.generate(model='llama3.1', prompt=f"Convert to 3-4 keywords: '{query.text}'. Output ONLY keywords.")
        keywords = kw_gen['response'].strip()
        
        # Step B: Search & Summarize
        raw_data = tools.web_research(keywords)
        final = ollama.chat(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': 'You are a shop assistant. Summarize the research into one concise sentence.'},
                {'role': 'user', 'content': f"Data: {raw_data}\n\nQuestion: {query.text}"}
            ]
        )
        return {"response": final.message.content}

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
