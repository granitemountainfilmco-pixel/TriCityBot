import re
import uvicorn
import ollama
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tools 
from database import init_db

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
init_db()

class ChatRequest(BaseModel):
    text: str

def route_command(user_input: str):
    user_input = user_input.lower().strip()

    # 1. LISTING & CHECKING (Priority)
    if any(k in user_input for k in ["list", "what are", "show", "check", "have", "stock"]):
        if "ticket" in user_input:
            return tools.list_tickets()
        
        # CLEANING the search term: remove command words to find the ITEM
        search_term = user_input
        for word in ["check", "inventory", "stock", "do we have", "any", "list", "what are"]:
            search_term = search_term.replace(word, "")
        search_term = search_term.strip()

        if not search_term:
            return tools.list_inventory()
        return tools.check_inventory(search_term)

    # 2. REMOVAL
    if any(k in user_input for k in ["remove", "delete"]):
        name = user_input.replace("remove", "").replace("delete", "").replace("the", "").strip()
        return tools.remove_from_inventory(name)

    # 3. TICKET LOGIC
    if "ticket" in user_input:
        res = ollama.generate(model='llama3.1', prompt=f"Extract task from: '{user_input}'. Output ONLY task.")
        return tools.create_ticket(res['response'].strip())

    # 4. REMINDER LOGIC
    if "remind" in user_input:
        res = ollama.chat(model='llama3.1', messages=[
            {'role': 'system', 'content': "Extract 'task' and 'time' from input. Format: TASK | TIME."},
            {'role': 'user', 'content': user_input}
        ])
        parts = res.message.content.split("|")
        task = parts[0].strip()
        time = parts[1].strip() if len(parts) > 1 else "ASAP"
        return tools.create_reminder(task, time)

    # 5. ADD LOGIC (Regex)
    add_match = re.search(r"add\s+(.*)\s+(?:for|at|is)?\s*[\$\s]*(\d+(?:\.\d{2})?)(?:\s+(?:qty|x)?\s*(\d+))?$", user_input)
    if add_match:
        name, price, qty = add_match.groups()
        return tools.add_to_inventory(name, price, int(qty) if qty else 1)

    # 6. RESEARCH
    if any(k in user_input for k in ["research", "find", "price"]):
        query = ollama.generate(model='llama3.1', prompt=f"Extract product from: {user_input}")['response'].strip()
        data = tools.web_research(query)
        summary = ollama.chat(model='llama3.1', messages=[
            {'role': 'system', 'content': "Summarize into 3 sentences. No lists."},
            {'role': 'user', 'content': f"FACTS: {data}"}], options={'temperature': 0.1})
        return summary.message.content

    return "Command not recognized. Try 'Shop add RTX 5090 2500'."

@app.post("/api/chat")
async def chat(req: ChatRequest):
    msg = req.text.lower().strip()
    for w in ["hey shop", "okay shop", "shop"]:
        if msg.startswith(w):
            return {"response": route_command(msg[len(w):].strip())}
    return {"response": ""} # Always return a string for the frontend

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
