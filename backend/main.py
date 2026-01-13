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
    # SYSTEM PROMPT: Optimized for Llama 3.1 to be a strict router
    system_prompt = """
    You are a Shop OS Router. Categorize the user's request into a tool command.
    OUTPUT ONLY THE COMMAND STRING. NO PROSE. NO EXPLANATIONS.
    
    Format: ACTION | SUBJECT | VALUE | QTY
    
    Actions:
    - LIST_INV (User wants to see all stock) -> LIST_INV | None | 0 | 0
    - CHECK_INV (User asks if an item is in stock) -> CHECK_INV | [item name] | 0 | 0
    - ADD_INV (User is adding items) -> ADD_INV | [item] | [price] | [qty]
    - REMOVE_INV (User is deleting an item) -> REMOVE_INV | [item] | 0 | 0
    - CREATE_TICKET (Work task/fix) -> CREATE_TICKET | [task] | 0 | 0
    - LIST_TICKETS (See work to do) -> LIST_TICKETS | None | 0 | 0
    - REMIND (Set a reminder) -> REMIND | [message] | [time] | 0
    - RESEARCH (Find info online) -> RESEARCH | [query] | 0 | 0
    
    If you don't understand, output: UNKNOWN | None | 0 | 0
    """

    try:
        # Temperature 0.1 makes the AI more consistent and robotic (good for routing)
        res = ollama.chat(model='llama3.1', messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_input}
        ], options={'temperature': 0.1})
        
        raw_output = res.message.content.strip()
        print(f"AI Router Output: {raw_output}") # Useful for debugging in terminal

        # Split and handle potential AI formatting errors
        parts = [p.strip() for p in raw_output.split("|")]
        if len(parts) < 4:
            # Fallback if AI forgets a pipe
            return "The AI router failed to format the command. Try rephrasing."

        action, subject, value, qty = parts[0], parts[1], parts[2], parts[3]

        # --- Tool Execution ---
        if action == "LIST_INV":
            return tools.list_inventory()
        
        elif action == "CHECK_INV":
            return tools.check_inventory(subject)
            
        elif action == "ADD_INV":
            # Strip '$' if the AI included it
            clean_price = value.replace('$', '').replace(',', '')
            return tools.add_to_inventory(subject, clean_price, int(qty) if qty.isdigit() else 1)
            
        elif action == "REMOVE_INV":
            return tools.remove_from_inventory(subject)
            
        elif action == "CREATE_TICKET":
            return tools.create_ticket(subject)
            
        elif action == "LIST_TICKETS":
            return tools.list_tickets()
            
        elif action == "REMIND":
            return tools.create_reminder(subject, value)
            
        elif action == "RESEARCH":
            web_data = tools.web_research(subject)
            summary = ollama.chat(model='llama3.1', messages=[
                {'role': 'system', 'content': "Summarize into 3 sentences. Objective tone."},
                {'role': 'user', 'content': f"Research data: {web_data}"}
            ])
            return summary.message.content

    except Exception as e:
        print(f"Error in Router: {e}")
        return "Internal Routing Error."

    return "Command not recognized. Try 'Shop add RTX 5090 2500'."

@app.post("/api/chat")
async def chat(req: ChatRequest):
    msg = req.text.lower().strip()
    trigger_words = ["hey shop", "okay shop", "shop"]
    
    remainder = None
    for w in trigger_words:
        if msg.startswith(w):
            remainder = msg[len(w):].strip()
            break
            
    if not remainder:
        return {"response": ""}

    response = route_command(remainder)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
