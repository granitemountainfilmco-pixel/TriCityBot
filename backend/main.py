@app.post("/api/chat")
async def chat(query: Query):
    user_input = query.text.lower()
    
    # 1. Expanded keyword list for better dictation accuracy
    inventory_keywords = ['add', 'ad', 'remove', 'delete', 'check', 'stock', 'inventory', 'have']
    
    if any(k in user_input for k in inventory_keywords):
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
        # Research Path
        kw_gen = ollama.generate(model='llama3.1', prompt=f"Keywords for: '{query.text}'. Max 3 words.")
        keywords = kw_gen['response'].strip()
        
        raw_data = tools.web_research(keywords)
        
        # We force a VERY short summary so the voice doesn't drone on
        final = ollama.chat(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': 'You are a shop assistant. Answer in one short sentence.'},
                {'role': 'user', 'content': f"Data: {raw_data}\n\nQuestion: {query.text}"}
            ]
        )
        return {"response": final.message.content}
