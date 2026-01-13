import sqlite3
from tavily import TavilyClient

# --- CONFIG ---
TAVILY_API_KEY = "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"
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def get_db_connection():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- TOOLS ---

def add_to_inventory(name: str, price: str, quantity: int = 1):
    try:
        clean_name = str(name).upper().strip()
        clean_price = float(str(price).replace("$", "").replace(",", "").strip())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert or Update (handles existing items)
        cursor.execute("""
            INSERT INTO inventory (name, price, quantity) 
            VALUES (?, ?, ?) 
            ON CONFLICT(name) DO UPDATE SET 
                quantity = quantity + EXCLUDED.quantity, 
                price = EXCLUDED.price
        """, (clean_name, clean_price, quantity))
        
        conn.commit()
        conn.close()
        return f"Successfully logged: {clean_name} at ${clean_price:,.2f} (x{quantity})."
    except Exception as e:
        # Prints real error to terminal for debugging
        print(f"DATABASE ERROR: {e}")
        return f"System Error: Could not save {name}. {str(e)}"

def check_inventory(term: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    fuzzy = f"%{term.upper().replace(' ', '%')}%"
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (fuzzy,))
    items = cursor.fetchall()
    conn.close()
    
    if not items:
        return f"I couldn't find '{term}' in your local inventory."
        
    res = "Inventory Matches:\n"
    for i in items:
        res += f"- {i['name']}: ${i['price']:,.2f} (Quantity: {i['quantity']})\n"
    return res

def list_inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    conn.close()
    
    if not items:
        return "The inventory is currently empty."
        
    res = "Current Stock:\n"
    for i in items:
        res += f"- {i['name']}: ${i['price']:,.2f} (x{i['quantity']})\n"
    return res

def remove_from_inventory(name: str):
    clean = str(name).upper().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ?", (clean,))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return f"Removed {clean}." if count > 0 else f"Item '{clean}' not found."

def web_research(query: str):
    try:
        print(f"Searching web for: {query}")
        response = tavily.search(query=query, search_depth="advanced", max_results=3)
        context = [f"Source: {r['url']} - Content: {r['content']}" for r in response['results']]
        return "\n".join(context)
    except Exception as e:
        return f"Research failed: {str(e)}"
