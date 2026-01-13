from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import tools

app = FastAPI()

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
    
    inventory_keywords = ['add', 'remove', 'delete', 'check', 'stock', 'inventory', 'have']
    
    try:
        if any(k in user_input for k in inventory_keywords):
            # PASS: Inventory Extraction
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': 'Extract product and price. If merged like "rtx5090500", split into Name="RTX 5090" and Price=500.'},
                    {'role': 'user', 'content': query.text}
                ],
                tools=[tools.add_to_inventory, tools.check_inventory, tools.remove_from_inventory]
            )
            
            if response.message.tool_calls:
                results = [getattr(tools, t.function.name)(**t.function.arguments) for t in response.message.tool_calls]
                return {"response": " ".join(results)}
            return {"response": response.message.content}

        else:
            # PASS: Free AI Research Summary
            # 1. Keyword Pass
            kw_res = ollama.generate(model='llama3.1', prompt=f"Convert to 3 search keywords: '{query.text}'. Output ONLY keywords.")
            keywords = kw_res['response'].strip()
            
            # 2. Web Pass
            web_data = tools.web_research(keywords)
            
            # 3. Summarization Pass
            summary = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': 'You are a shop assistant. Summarize the web data into one short, helpful sentence.'},
                    {'role': 'user', 'content': f"Web Data: {web_data}\n\nUser Question: {query.text}"}
                ]
            )
            return {"response": summary.message.content}

    except Exception as e:
        return {"response": "I encountered a processing error."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
