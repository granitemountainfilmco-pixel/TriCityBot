from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
from contextlib import asynccontextmanager
from database import init_db
import tools

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    print(f"Heard: {query.text}") # Look for this in terminal!
    
    tools_map = {
        'add_to_inventory': tools.add_to_inventory,
        'remove_from_inventory': tools.remove_from_inventory,
        'check_inventory': tools.check_inventory,
        'web_research': tools.web_research,
        'check_shipping_status': tools.check_shipping_status
    }

    try:
        response = ollama.chat(
            model='llama3.1',
            messages=[{'role': 'user', 'content': query.text}],
            tools=[tools.add_to_inventory, tools.remove_from_inventory, 
                   tools.check_inventory, tools.web_research, tools.check_shipping_status]
        )

        if response.message.tool_calls:
            results = []
            for tool in response.message.tool_calls:
                func = tools_map.get(tool.function.name)
                if func:
                    results.append(func(**tool.function.arguments))
            return {"response": ". ".join(results)}
        
        return {"response": response.message.content}
    except Exception as e:
        print(f"Ollama Error: {e}")
        return {"response": "I can't talk to the AI brain right now. Is Ollama running?"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
