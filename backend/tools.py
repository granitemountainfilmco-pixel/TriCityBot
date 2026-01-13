import os
import sqlite3
from tavily import TavilyClient

# --- CONFIGURATION ---
TAVILY_API_KEY = "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"  # Get this from tavily.com
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def get_db_connection():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn\

def list_inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, quantity FROM inventory")
    items = cursor.fetchall()
    conn.close()

    if not items:
        return "Inventory is empty."

    return "Inventory:\n" + "\n".join(
        f"{i['name']} (${i['price']:,.2f}) x{i['quantity']}"
        for i in items
    )


# --- INVENTORY TOOLS ---
def add_to_inventory(name: str, price: str, quantity: int = 1):
    try:
        clean_name = str(name).upper().strip()
        # Remove '$' and commas to turn "2,500" into 2500.0
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
        return f"Successfully logged: {clean_name} at ${clean_price:,.2f}."
    except Exception as e:
        return f"Failed to log item. Price '{price}' is invalid."

def check_inventory(query: str):
    # Standardize the search term
    term = str(query).upper().replace("CHECK ", "").replace("STOCK ", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fuzzy search: Finds "RTX 5090" even if the query is "rtx5090"
    fuzzy = f"%{term.replace(' ', '%')}%"
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (fuzzy,))
    items = cursor.fetchall()
    conn.close()
    if not items: return f"I couldn't find '{term}' in your local inventory."
    return "Inventory Match: " + ", ".join([f"{i['name']} (${i['price']:,.2f})" for i in items])

def remove_from_inventory(name: str):
    clean = str(name).upper().strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ?", (clean,))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return f"Deleted {clean}." if count > 0 else f"Item '{clean}' not found."

# --- RESEARCH TOOLS ---
def web_research(query: str):
    """Fetches real-time market data to prevent AI hallucinations."""
    try:
        print(f"Tavily Fetching: {query}")
        # Search depth 'advanced' gives more factual snippets for prices
        response = tavily.search(query=query, search_depth="advanced", max_results=3)
        
        context = []
        for r in response['results']:
            context.append(f"Source: {r['title']}\nContent: {r['content']}")
        
        return "\n---\n".join(context) if context else "No web results found."
    except Exception as e:
        return f"Web search error: {str(e)}"
