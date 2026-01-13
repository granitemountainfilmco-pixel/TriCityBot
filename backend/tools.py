import os
from tavily import TavilyClient
from database import get_db_connection

# Get your key from tavily.com (Free tier: 1000 searches/mo)
TAVILY_API_KEY = "tvly-YOUR_ACTUAL_API_KEY_HERE"
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def add_to_inventory(name: str, price: str, quantity: int = 1):
    try:
        clean_name = str(name).upper().replace("ADD ", "").strip()
        clean_price = float(str(price).replace("$", "").replace(",", "").strip())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (name, price, quantity) 
            VALUES (?, ?, ?) 
            ON CONFLICT(name) DO UPDATE SET quantity = quantity + ?, price = ?
        """, (clean_name, clean_price, quantity, quantity, clean_price))
        conn.commit()
        conn.close()
        return f"Confirmed: {clean_name} added at ${clean_price}."
    except Exception as e:
        return f"Error: Could not parse '{price}' as a valid price."

def check_inventory(query: str):
    term = str(query).upper().replace("CHECK ", "").replace("STOCK ", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    # Uses SQL wildcards to find "RTX 5090" even if input is "RTX5090"
    fuzzy = term.replace("RTX", "RTX%")
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{fuzzy}%",))
    items = cursor.fetchall()
    conn.close()
    if not items: return f"I have no record of {term} in our stock."
    return "Stock Found: " + ", ".join([f"{i['name']} (${i['price']})" for i in items])

def remove_from_inventory(name: str):
    clean = str(name).upper().replace("REMOVE ", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name LIKE ?", (f"%{clean}%",))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return f"Removed {clean} from system." if count > 0 else f"Item {clean} not found."

def web_research(query: str):
    """The new 'Anti-Hallucination' search logic."""
    try:
        print(f"DEBUG: Tavily fetching for: {query}")
        # search_depth="advanced" ensures it finds actual prices/specs
        response = tavily.search(query=query, search_depth="advanced", max_results=3)
        
        context = []
        for r in response['results']:
            context.append(f"Title: {r['title']}\nSnippet: {r['content']}")
        
        if not context:
            return "No current market data found on the web."
            
        return "\n---\n".join(context)
    except Exception as e:
        print(f"Tavily Error: {e}")
        return "Search Service currently unavailable."
