from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import tools
from database import init_db

# 1. INITIALIZE THE APP (This fixes your NameError)
app = FastAPI()

# 2. SETUP MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

# 3. DEFINE ROUTES
@app.post("/api/chat")
async def chat(query: Query):
    user_input = query.text.lower()
    print(f"Heard: {user_input}")
    
    inventory_keywords = ['add', 'remove', 'delete', 'check', 'stock', 'inventory', 'have']
    
    try:
        if any(k in user_input for k in inventory_keywords):
            # Local Database Path
            response = ollama.chat(
                model='llama3.1',
                messages=[{'role': 'user', 'content': query.text}],
                tools=[tools.add_to_inventory, tools.check_inventory, tools.remove_from_inventory]
            )
            
            if response.message.tool_calls:
                results = []
                for tool in response.message.tool_calls:
                    func = getattr(tools, tool.function.name)
                    results.append(func(**tool.function.arguments))
                return {"response": " ".join(results)}
            return {"response": response.message.content}

        else:
            # Deep Research Path
            kw_gen = ollama.generate(model='llama3.1', prompt=f"Keywords for: '{query.text}'. Max 3 words.")
            keywords = kw_gen['response'].strip()
            
            raw_data = tools.web_research(keywords)
            
            final = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': 'You are a shop assistant. Answer in one short sentence.'},
                    {'role': 'user', 'content': f"Data: {raw_data}\n\nQuestion: {query.text}"}
                ]
            )
            return {"response": final.message.content}
            
    except Exception as e:
        print(f"Server Error: {e}")
        return {"response": "I encountered an internal error. Please check the backend console."}

# 4. START THE SERVER
if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
