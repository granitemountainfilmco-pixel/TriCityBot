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

    # 1. LISTING LOGIC (Priority)
    if any(k in user_input for k in ["list", "what are", "show me", "check"]):
        if "ticket" in user_input:
            return tools.list_tickets()
        if any(k in user_input for k in ["inventory", "stock", "have"]):
            kw = ollama.generate(model='llama3.1', prompt=f"Extract product name from: '{user_input}'. Output only the name.")
            name = kw['response'].strip()
            if name and name != "none":
                return tools.check_inventory(name)
            return tools.list_inventory()

    # 2. REMOVAL LOGIC
    if any(k in user_input for k in ["remove", "delete"]):
        name = user_input.replace("remove", "").replace("delete", "").replace("the", "").strip()
        return tools.remove_from_inventory(name)

    # 3. TICKET LOGIC
    if "ticket" in user_input:
        res = ollama.generate(model='llama3.1', prompt=f"Extract the core work task from: '{user_input}'. Output ONLY the task.")
        return tools.create_ticket(res['response'].strip())

    # 4. REMINDER LOGIC (RESTORED)
    if "remind" in user_input:
        res = ollama.chat(model='llama3.1', messages=[
            {'role': 'system', 'content': "Extract 'task' and 'time' from input. Format: TASK | TIME. If no time, use 'ASAP'."},
            {'role': 'user', 'content': user_input}
        ])
        # Splits the AI response into Task and Time
        if "|" in res.message.content:
            parts = res.message.content.split("|")
            task = parts[0].strip()
            time = parts[1].strip()
        else:
            task = res.message.content.strip()
            time = "ASAP"
        return tools.create_reminder(task, time)

    # 5. ADD LOGIC (Greedy Regex)
    add_match = re.search(r"add\s+(.*)\s+(?:for|at|is)?\s*[\$\s]*(\d+(?:\.\d{2})?)(?:\s+(?:qty|x)?\s*(\d+))?$", user_input)
    if add_match:
        name, price, qty = add_match.groups()
        return tools.add_to_inventory(name, price, int(qty) if qty else 1)

    # 6. RESEARCH
    if any(k in user_input for k in ["research", "find", "price"]):
        topic_gen = ollama.generate(model='llama3.1', prompt=f"Extract product name from: '{user_input}'.")
        query = topic_gen['response'].strip()
        web_data = tools.web_research(query)
        summary = ollama.chat(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': "Summarize FACTS into EXACTLY 3 sentences. No lists. Objective tone."},
                {'role': 'user', 'content': f"FACTS: {web_data}\n\nSummarize for {query}"}
            ],
            options={'temperature': 0.1}
        )
        return summary.message.content

    return "Command not recognized. Try 'add RTX 5090 2500' or 'make a ticket for the broken gpu'."

@app.post("/api/chat")
async def chat(req: ChatRequest):
    msg = req.text.lower().strip()
    trigger_words = ["hey shop", "okay shop", "shop"]
    
    remainder = None
    for w in trigger_words:
        if msg.startswith(w):
            remainder = msg[len(w):].strip()
            break
            
    # If no wake word is found, we return an empty response string.
    # This prevents the frontend from "hanging" while waiting for a reply.
    if not remainder:
        return {"response": ""}

    response = route_command(remainder)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
