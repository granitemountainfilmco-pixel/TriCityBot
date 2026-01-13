import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama, tools
from database import init_db

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
init_db()

class Query(BaseModel): text: str

# Define tool schemas for Ollama 3.1+
INVENTORY_TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'check_inventory',
            'description': 'Check if an item exists in the local shop inventory.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'description': 'The name of the item to look for.'},
                },
                'required': ['query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'remove_from_inventory',
            'description': 'Remove an item from the shop inventory database.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'The exact name of the item to delete.'},
                },
                'required': ['name'],
            },
        },
    }
]

@app.post("/api/chat")
async def chat(query: Query):
    user_input = query.text.strip().lower()
    trigger_words = ["hey shop", "assistant", "okay shop", "shop"]
    
    # Improved Trigger Check: Check if any trigger word exists anywhere in the start
    is_triggered = any(word in user_input for word in trigger_words)
    if not is_triggered:
        return {"response": ""}

    # Clean the input: remove the trigger word and leading/trailing junk
    for word in trigger_words:
        user_input = user_input.replace(word, "").strip()

    # 1. FIXED Regex: Handles "2500 dollars" or "at 2500" more gracefully
    add_match = re.search(r"add\s+(.+?)\s*(?:for|at|is|price)?\s*[\$\s]*(\d+)", user_input)
    if add_match:
        name, price = add_match.groups()
        return {"response": tools.add_to_inventory(name, price)}

    # 2. FIXED Tool Logic: Only trigger tools if keywords match
    if any(k in user_input for k in ['check', 'stock', 'inventory', 'have', 'delete', 'remove']):
        response = ollama.chat(
            model='llama3.1',
            messages=[{'role': 'user', 'content': user_input}],
            tools=INVENTORY_TOOLS
        )
        
        if response.message.tool_calls:
            results = []
            for tool in response.message.tool_calls:
                # Map the string name to the actual function in tools.py
                func = getattr(tools, tool.function.name)
                results.append(func(**tool.function.arguments))
            return {"response": " ".join(results)}
        
        # Fallback if AI didn't call a tool but should have
        return {"response": "I'm not sure which item you're referring to in the inventory."}

    # 3. Research Path
    kw_gen = ollama.generate(model='llama3.1', prompt=f"Provide 3 search keywords for: '{user_input}'. Output only keywords.")
    web_data = tools.web_research(kw_gen['response'].strip())
    
    summary = ollama.chat(
        model='llama3.1',
        messages=[{
            'role': 'system', 
            'content': f"FACTS: {web_data}\nINSTRUCTION: Answer in ONE sentence (max 20 words). Use the facts provided."
        }, {'role': 'user', 'content': user_input}]
    )
    return {"response": summary.message.content}
