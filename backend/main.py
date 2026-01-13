import uvicorn
import ollama
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tools 
from database import init_db
import re

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
init_db()

class ChatRequest(BaseModel):
    text: str

def route_command(user_input: str):
    # Use the AI to determine the INTENT and the DATA
    system_prompt = """
    You are a shop assistant router. Analyze the user's request and categorize it.
    Output ONLY the categorized command in this format: 
    ACTION | ITEM_OR_TASK | PRICE | QTY
    
    Actions: LIST_INV, CHECK_INV, ADD_INV, REMOVE_INV, CREATE_TICKET, LIST_TICKETS, REMIND, RESEARCH, UNKNOWN
    
    Examples:
    - "What's in my inventory?" -> LIST_INV | None | 0 | 0
    - "Do we have 5090s?" -> CHECK_INV | 5090 | 0 | 0
    - "Add a 4090 for 1200" -> ADD_INV | 4090 | 1200 | 1
    - "Create a ticket to fix the sink" -> CREATE_TICKET | fix the sink | 0 | 0
    - "Remind me to call Bob at 5pm" -> REMIND | call Bob | 5pm | 0
    """

    res = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_input}
    ])
    
    # Parse the AI response
    try:
        parts = res.message.content.split("|")
        action = parts[0].strip()
        subject = parts[1].strip()
        price_or_time = parts[2].strip()
        qty = parts[3].strip() if len(parts) > 3 else "1"

        # Route to the existing tools.py functions
        if action == "LIST_INV":
            return tools.list_inventory()
        
        elif action == "CHECK_INV":
            return tools.check_inventory(subject)
            
        elif action == "ADD_INV":
            return tools.add_to_inventory(subject, price_or_time, int(qty))
            
        elif action == "REMOVE_INV":
            return tools.remove_from_inventory(subject)
            
        elif action == "CREATE_TICKET":
            return tools.create_ticket(subject)
            
        elif action == "LIST_TICKETS":
            return tools.list_tickets()
            
        elif action == "REMIND":
            return tools.create_reminder(subject, price_or_time)
            
        elif action == "RESEARCH":
            data = tools.web_research(subject)
            summary = ollama.chat(model='llama3.1', messages=[
                {'role': 'system', 'content': "Summarize into 3 sentences."},
                {'role': 'user', 'content': data}
            ])
            return summary.message.content
            
    except Exception as e:
        print(f"Routing Error: {e}")
        
    return "I understood the request but couldn't process the tool. Try again."

@app.post("/api/chat")
async def chat(req: ChatRequest):
    msg = req.text.lower().strip()
    # Simple check for wake words to avoid unnecessary AI calls
    for w in ["hey shop", "okay shop", "shop"]:
        if msg.startswith(w):
            return {"response": route_command(msg[len(w):].strip())}
    return {"response": ""}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
