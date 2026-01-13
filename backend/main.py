from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import tools
from database import init_db

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    print(f"User Input: {query.text}")
    
    # PASS 1: Keyword Extraction (The 'Sorting' Layer)
    # This turns "Hey can you find the price for a 4090" into "RTX 4090 price"
    kw_prompt = f"Convert this to 3 search keywords: '{query.text}'. Output ONLY the keywords."
    keywords = ollama.generate(model='llama3.1', prompt=kw_prompt)['response'].strip()
    
    # PASS 2: Intent Routing
    text_lower = query.text.lower()
    local_cmds = ['add', 'remove', 'delete', 'check', 'inventory', 'stock']
    
    if any(cmd in text_lower for cmd in local_cmds):
        # Local Tool Path
        response = ollama.chat(
            model='llama3.1',
            messages=[{'role': 'user', 'content': query.text}],
            tools=[tools.add_to_inventory, tools.check_inventory, tools.remove_from_inventory]
        )
        
        # Tool Execution Logic
        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                func = getattr(tools, tool.function.name)
                return {"response": func(**tool.function.arguments)}
        
        return {"response": response.message.content}
    
    # PASS 3: Deep Research Path
    raw_research = tools.web_research(keywords)
    summary = ollama.chat(
        model='llama3.1',
        messages=[
            {'role': 'system', 'content': 'You are a shop assistant. Summarize the research data into one concise, professional sentence.'},
            {'role': 'user', 'content': f"Data: {raw_research}\n\nQuestion: {query.text}"}
        ]
    )
    return {"response": summary.message.content}

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
