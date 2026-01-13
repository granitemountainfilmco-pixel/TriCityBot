from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
from contextlib import asynccontextmanager # Added for lifespan
from database import init_db
from tools import (
    add_to_inventory, 
    remove_from_inventory, 
    check_inventory, 
    web_research,
    check_shipping_status
)

# 1. Modern Lifespan Handler (Replaces @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    init_db()
    print("Database initialized and ready.")
    yield
    # This runs when the server stops
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Allow Frontend to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    print(f"User: {query.text}")

    tools_map = {
        'add_to_inventory': add_to_inventory,
        'remove_from_inventory': remove_from_inventory,
        'check_inventory': check_inventory,
        'web_research': web_research,
        'check_shipping_status': check_shipping_status
    }

    response = ollama.chat(
        model='llama3.1',
        messages=[{'role': 'user', 'content': query.text}],
        tools=list(tools_map.values())
    )

    final_response = ""
    
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            fname = tool.function.name
            args = tool.function.arguments
            print(f"Tool Call: {fname} {args}")
            
            if fname in tools_map:
                result = tools_map[fname](**args)
                final_response = result
            else:
                final_response = "Error: Tool not found."
    else:
        final_response = response.message.content

    return {"response": final_response}

# Entry point for python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
