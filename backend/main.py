from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import tools
from database import init_db

app = FastAPI()

# Enable CORS so the React frontend can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    user_input = query.text.lower()
    print(f"--- Processing Request: {user_input} ---")
    
    # 1. DEFINE LOCAL COMMAND TRIGGERS
    # If any of these words are present, we look at the local database first.
    inventory_keywords = ['add', 'remove', 'delete', 'check', 'inventory', 'stock', 'list', 'have']
    
    if any(k in user_input for k in inventory_keywords):
        print("Intent: Local Inventory")
        try:
            # Pass 1: AI decides which inventory tool to use
            response = ollama.chat(
                model='llama3.1',
                messages=[{'role': 'user', 'content': query.text}],
                tools=[
                    tools.add_to_inventory, 
                    tools.check_inventory, 
                    tools.remove_from_inventory
                ]
            )
            
            # Execute the tool if the AI called one
            if response.message.tool_calls:
                results = []
                for tool in response.message.tool_calls:
                    # Dynamically find the function in tools.py
                    func_name = tool.function.name
                    if hasattr(tools, func_name):
                        print(f"Executing Tool: {func_name}")
                        func = getattr(tools, func_name)
                        result = func(**tool.function.arguments)
                        results.append(result)
                return {"response": " ".join(results)}
            
            # If AI didn't call a tool but thought it was inventory, return its text
            return {"response": response.message.content}
            
        except Exception as e:
            print(f"Inventory Error: {e}")
            return {"response": "I had trouble accessing the shop database."}

    # 2. RESEARCH PATH (The "Deep Research" Agentic Flow)
    else:
        print("Intent: Web Research")
        try:
            # Pass 1: Extract high-quality search keywords from conversational speech
            kw_prompt = f"Convert this request into 3-4 professional search engine keywords. Output ONLY keywords: '{query.text}'"
            kw_gen = ollama.generate(model='llama3.1', prompt=kw_prompt)
            keywords = kw_gen['response'].strip()
            print(f"Extracted Keywords: {keywords}")

            # Pass 2: Get raw data from the web tool
            raw_data = tools.web_research(keywords)

            # Pass 3: AI Summarization of results
            summary_prompt = (
                f"You are a technical shop assistant. Using the research data provided below, "
                f"answer the owner's question: '{query.text}'. "
                f"Provide a concise, professional one or two-sentence summary."
            )
            
            final_summary = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': summary_prompt},
                    {'role': 'user', 'content': f"Research Data: {raw_data}"}
                ]
            )
            return {"response": final_summary.message.content}

        except Exception as e:
            print(f"Research Error: {e}")
            return {"response": "I attempted to research that but the search service is unavailable."}

# Initialize the database and run the server
if __name__ == "__main__":
    init_db()  # Creates the inventory table if it doesn't exist
    import uvicorn
    print("Shop OS Backend is live on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
