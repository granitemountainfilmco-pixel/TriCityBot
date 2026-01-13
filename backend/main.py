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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    tools_map = {
        'add_to_inventory': tools.add_to_inventory,
        'remove_from_inventory': tools.remove_from_inventory,
        'check_inventory': tools.check_inventory,
        'web_research': tools.web_research,
        'check_shipping_status': tools.check_shipping_status
    }

    # Prompt engineering to help the AI use keywords for research
    system_prompt = "You are a computer shop assistant. If researching, use short keywords."
    
    response = ollama.chat(
        model='llama3.1',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query.text}
        ],
        tools=[tools.add_to_inventory, tools.remove_from_inventory, 
               tools.check_inventory, tools.web_research, tools.check_shipping_status]
    )

    if response.message.tool_calls:
        tool_results = []
        for tool in response.message.tool_calls:
            func = tools_map.get(tool.function.name)
            if func:
                result = func(**tool.function.arguments)
                tool_results.append(result)
        return {"response": "\n".join(tool_results)}
    
    return {"response": response.message.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
