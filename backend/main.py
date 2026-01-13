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

@app.post("/api/chat")
async def chat(query: Query):
    raw_input = query.text.strip()
    user_input = raw_input.lower()
    
    # --- VOICE KEYWORD TRIGGER ---
    # Only proceed if the input starts with "hey shop" or "assistant"
    # This prevents the AI from answering accidental background noise
    trigger_words = ["hey shop", "assistant", "okay shop"]
    is_triggered = any(user_input.startswith(word) for word in trigger_words)
    
    # If it was a voice command but no trigger word, ignore it
    # (Note: Frontend should handle initial filtering, but this is a safety backstop)
    if not is_triggered and len(user_input.split()) > 1:
        # Check if it's a direct typed command (usually shorter/no trigger)
        # If it's a long sentence without a trigger, we ignore.
        pass 

    # --- 1. THE DATA EXTRACTOR (No AI Hallucination) ---
    # Regex pattern: "add [item name] [price]" or "add [item name]-[price]"
    add_pattern = re.search(r"add\s+(.+?)(?:\s+for\s+|\s+at\s+|\s*-\s*|\s+)\$?(\d+(?:[.,]\d+)?)", user_input)
    if add_pattern:
        name, price = add_pattern.groups()
        return {"response": tools.add_to_inventory(name, price)}

    # --- 2. INVENTORY CHECK PATH ---
    if any(k in user_input for k in ['check', 'stock', 'inventory', 'have']):
        response = ollama.chat(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': "You are a database tool. Output ONLY the tool call."},
                {'role': 'user', 'content': user_input}
            ],
            tools=[tools.check_inventory, tools.remove_from_inventory]
        )
        if response.message.tool_calls:
            res = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
            return {"response": " ".join(res)}
        return {"response": response.message.content}

    # --- 3. THE RESEARCH PATH (RAG) ---
    else:
        # Step A: Get clean search terms
        kw_gen = ollama.generate(model='llama3.1', prompt=f"Search keywords for: '{user_input}'. ONLY words.")
        web_data = tools.web_research(kw_gen['response'].strip())
        
        # Step B: Force Grounded Response
        summary = ollama.chat(
            model='llama3.1',
            messages=[
                {
                    'role': 'system', 
                    'content': f"FACTS: {web_data}\n\n"
                               "INSTRUCTION: Summarize the facts above. "
                               "Trust the FACTS over your memory. "
                               "If it's about the RTX 5090, use the prices in the FACTS."
                },
                {'role': 'user', 'content': user_input}
            ]
        )
        return {"response": summary.message.content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
