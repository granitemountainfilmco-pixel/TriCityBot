from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
from database import init_db
from tools import (
    add_to_inventory, 
    remove_from_inventory, 
    check_inventory, 
    web_research,
    check_shipping_status
)

app = FastAPI()

# Allow Frontend to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    print(f"User: {query.text}")

    # 1. Available Tools
    tools_map = {
        'add_to_inventory': add_to_inventory,
        'remove_from_inventory': remove_from_inventory,
        'check_inventory': check_inventory,
        'web_research': web_research,
        'check_shipping_status': check_shipping_status
    }

    # 2. First Pass: Ask Ollama
    response = ollama.chat(
        model='llama3.1', # Make sure you have this model pulled!
        messages=[{'role': 'user', 'content': query.text}],
        tools=list(tools_map.values())
    )

    final_response = ""
    
    # 3. Check for Tool Calls
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            fname = tool.function.name
            args = tool.function.arguments
            print(f"🛠️ Tool Call: {fname} {args}")
            
            if fname in tools_map:
                # Execute Python Function
                result = tools_map[fname](**args)
                final_response = result
            else:
                final_response = "Error: Tool not found."
    else:
        # No tool needed, just conversation
        final_response = response.message.content

    return {"response": final_response}
