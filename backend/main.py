from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
from contextlib import asynccontextmanager
from database import init_db
import tools

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    print(f"User Request: {query.text}")
    
    tools_list = [
        tools.add_to_inventory, 
        tools.remove_from_inventory, 
        tools.check_inventory, 
        tools.web_research, 
        tools.check_shipping_status
    ]

    try:
        # Pass 1: Initial AI thinking
        response = ollama.chat(
            model='llama3.1',
            messages=[{'role': 'user', 'content': query.text}],
            tools=tools_list
        )

        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                func_name = tool.function.name
                func_args = tool.function.arguments
                
                # Execute the correct tool
                if hasattr(tools, func_name):
                    func = getattr(tools, func_name)
                    raw_result = func(**func_args)
                    
                    # Pass 2: AI Summarization (The "Sorting" Pass)
                    summary_call = ollama.chat(
                        model='llama3.1',
                        messages=[
                            {'role': 'system', 'content': 'You are a shop assistant. Summarize the following data into a short, spoken sentence for the owner.'},
                            {'role': 'user', 'content': f"Context: {query.text}\n\nRaw Data: {raw_result}"}
                        ]
                    )
                    return {"response": summary_call.message.content}
        
        return {"response": response.message.content}
    except Exception as e:
        print(f"Ollama Error: {e}")
        return {"response": "I encountered an error processing that. Please check if Ollama is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
