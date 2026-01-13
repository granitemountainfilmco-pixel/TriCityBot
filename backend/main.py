from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import tools
from database import init_db

# 1. INITIALIZE APP & DATABASE
app = FastAPI()

# Enable CORS so the Frontend can talk to the Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# [cite_start]Create the inventory table if it doesn't exist [cite: 1]
init_db()

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    # 2. PHONETIC SCRUBBER
    # Fixes common voice-to-text hallucinations before they hit the AI or Database
    user_input = query.text.lower()
    user_input = user_input.replace("or tx", "rtx") \
                           .replace("forty ninety", "4090") \
                           .replace("fifty ninety", "5090") \
                           .replace("five zero nine zero", "5090")

    print(f"User Said: {query.text}")
    print(f"Sanitized: {user_input}")

    # Keywords that trigger the local database logic
    inventory_keywords = ['add', 'remove', 'delete', 'check', 'stock', 'inventory', 'have']
    
    try:
        # 3. INVENTORY PATH (Local SQLite)
        if any(k in user_input for k in inventory_keywords):
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {
                        'role': 'system', 
                        'content': 'You are a precise inventory assistant. Extract "name" and "price". '
                                   'If the user says "rtx50902500", split it into Name="RTX 5090" and Price=2500. '
                                   'Always strip action words like "add" or "check" from the product name.'
                    },
                    {'role': 'user', 'content': user_input}
                ],
                tools=[tools.add_to_inventory, tools.check_inventory, tools.remove_from_inventory]
            )
            
            # Execute the tool if the AI decided to use one
            if response.message.tool_calls:
                results = []
                for tool in response.message.tool_calls:
                    func = getattr(tools, tool.function.name)
                    results.append(func(**tool.function.arguments))
                return {"response": " ".join(results)}
            
            return {"response": response.message.content}

        # 4. RESEARCH PATH (Web Search + Local AI Summary)
        else:
            # Pass A: Extract clean search keywords from messy speech
            kw_gen = ollama.generate(
                model='llama3.1', 
                prompt=f"Extract 3 technical search keywords from this request: '{user_input}'. Output ONLY keywords."
            )
            keywords = kw_gen['response'].strip()
            
            # [cite_start]Pass B: Get real-time data from the web [cite: 3]
            raw_web_data = tools.web_research(keywords)
            
            # Pass C: Summarize using the web data as the ONLY source of truth
            final_response = ollama.chat(
                model='llama3.1',
                messages=[
                    {
                        'role': 'system', 
                        'content': 'You are a real-time shop researcher. IGNORE your internal knowledge about product release dates. '
                                   'ONLY use the provided Web Data to answer. If the Web Data contains prices for a product, '
                                   'the product exists. Summarize the findings in one concise sentence.'
                    },
                    {'role': 'user', 'content': f"Web Data: {raw_web_data}\n\nUser Question: {user_input}"}
                ]
            )
            return {"response": final_response.message.content}
            
    except Exception as e:
        print(f"Error in main loop: {e}")
        return {"response": "I'm having trouble processing that right now. Check the backend console."}

# 5. START SERVER
if __name__ == "__main__":
    import uvicorn
    # [cite_start]Make sure your start_shop.bat [cite: 2] points to this port
    uvicorn.run(app, host="0.0.0.0", port=8000)
