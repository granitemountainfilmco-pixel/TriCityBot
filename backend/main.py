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
    user_input = query.text.lower()
    print(f"Heard: {user_input}")
    
    inventory_keywords = ['add', 'remove', 'delete', 'check', 'stock', 'inventory', 'have']
    
    try:
        if any(k in user_input for k in inventory_keywords):
            # EXTRACTION MODE: Helps AI split merged words like 'rtx5090500'
            response = ollama.chat(
                model='llama3.1',
                messages=[
                    {
                        'role': 'system', 
                        'content': 'You are a shop inventory expert. If product names and prices are merged in the text, split them. '
                                   'Example: "rtx3080500" means Name="RTX 3080", Price=500.'
                    },
                    {'role': 'user', 'content': query.text}
                ],
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
            # RESEARCH PATH
            kw_gen = ollama.generate(model='llama3.1', prompt=f"Extract 3 keywords: '{query.text}'")
            keywords = kw_gen['response'].strip()
            raw_data = tools.web_research(keywords)
            final = ollama.chat(
                model='llama3.1',
                messages=[
                    {'role': 'system', 'content': 'Summarize the data into one professional sentence.'},
                    {'role': 'user', 'content': f"Data: {raw_data}\nQ: {query.text}"}
                ]
            )
            return {"response": final.message.content}
            
    except Exception as e:
        return {"response": f"Server Error: {str(e)}"}

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
