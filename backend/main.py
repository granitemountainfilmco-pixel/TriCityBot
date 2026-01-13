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

# Ensure DB is ready on startup
init_db()

class ChatRequest(BaseModel):
    text: str

def route_command(user_input: str):
    user_input = user_input.lower().strip()

    # 1. REMOVAL LOGIC (Highest Priority)
    if any(k in user_input for k in ["remove", "delete"]):
        # Remove trigger word and "the" to get the clean item name
        name = user_input.replace("remove", "").replace("delete", "").replace("the", "").strip()
        return tools.remove_from_inventory(name)

    # 2. TICKET LOGIC
    if "ticket" in user_input:
        res = ollama.generate(model='llama3.1', prompt=f"Extract the core work task from: '{user_input}'. Output ONLY the task.")
        return tools.create_ticket(res['response'].strip())

    # 3. REMINDER LOGIC
    if "remind" in user_input:
        res = ollama.chat(model='llama3.1', messages=[
            {'role': 'system', 'content': "Extract 'task' and 'time' from input. Format: TASK | TIME. Example: 'fix sink | 5pm'"},
            {'role': 'user', 'content': user_input}
        ])
        parts = res.message.content.split("|")
        task = parts[0].strip()
        time = parts[1].strip() if len(parts) > 1 else "ASAP"
        return tools.create_reminder(task, time)

    # 4. ADD LOGIC (Greedy Regex)
    add_match = re.search(r"add\s+(.*)\s+(?:for|at|is)?\s*[\$\s]*(\d+(?:\.\d{2})?)(?:\s+(?:qty|x)?\s*(\d+))?$", user_input)
    if add_match:
        name, price, qty = add_match.groups()
        return tools.add_to_inventory(name, price, int(qty) if qty else 1)

    # 5. LISTING/CHECKING
    if "list" in user_input:
        if "ticket" in user_input: return tools.list_tickets()
        return tools.list_inventory()
    
    if any(k in user_input for k in ["check", "stock", "have"]):
        kw = ollama.generate(model='llama3.1', prompt=f"Extract product name from: '{user_input}'.")
        return tools.check_inventory(kw['response'].strip())

    # 6. RESEARCH (3-Sentence Limit)
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

    return "Command not recognized. Try 'add RTX 5090 2500' or 'remove RTX 5090'."

@app.post("/api/chat")
async def chat(req: ChatRequest):
    msg = req.text.lower().strip()
    trigger_words = ["hey shop", "okay shop", "shop"]
    remainder = None
    for w in trigger_words:
        if msg.startswith(w):
            remainder = msg[len(w):].strip()
            break
            
    if not remainder: return {"response": None}
    return {"response": route_command(remainder)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
