from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import tools
from database import init_db  # Import the fix

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize the database table before the server accepts requests
init_db()

class Query(BaseModel):
    text: str

@app.post("/api/chat")
async def chat(query: Query):
    user_input = query.text.lower()
    inv_keys = ['add', 'remove', 'delete', 'check', 'stock', 'inventory', 'have']
    try:
        if any(k in user_input for k in inv_keys):
            response = ollama.chat(
                model='llama3.1', 
                messages=[
                    {'role': 'system', 'content': 'Split merged product/price like "rtx5090500" into Name="RTX 5090", Price=500.'}, 
                    {'role': 'user', 'content': query.text}
                ], 
                tools=[tools.add_to_inventory, tools.check_inventory, tools.remove_from_inventory]
            )
            if response.message.tool_calls:
                res = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
                return {"response": " ".join(res)}
            return {"response": response.message.content}
        else:
            kw = ollama.generate(model='llama3.1', prompt=f"Keywords for: '{query.text}'")['response'].strip()
            data = tools.web_research(kw)
            summary = ollama.chat(
                model='llama3.1', 
                messages=[
                    {'role': 'system', 'content': 'Summarize research in one short sentence.'}, 
                    {'role': 'user', 'content': f"Data: {data}\nQ: {query.text}"}
                ]
            )
            return {"response": summary.message.content}
    except Exception as e:
        print(f"Error: {e}")
        return {"response": "Processing error."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
