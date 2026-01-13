import sqlite3
from database import get_db_connection
from duckduckgo_search import DDGS

def add_to_inventory(name: str, price: float, quantity: int = 1, notes: str = ""):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventory (name, price, quantity, notes) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET quantity = quantity + ?",
            (name, price, quantity, notes, quantity)
        )
        conn.commit()
        conn.close()
        return f"Database updated: {name} is now in stock at ${price}."
    except Exception as e:
        return f"Inventory error: {str(e)}"

def remove_from_inventory(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ?", (name,))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return f"Successfully removed {name}." if count > 0 else f"Item {name} not found."

def check_inventory(query: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{query}%",))
    items = cursor.fetchall()
    conn.close()
    if not items: return "The item is not in our records."
    return "Stock Status: " + ", ".join([f"{i['name']} (${i['price']})" for i in items])

def web_research(query: str):
    """
    Enhanced research tool with error handling and better formatting.
    """
    try:
        print(f"DEBUG: Starting web research for: {query}")
        
        # We use short keywords for better search engine hits
        search_results = []
        with DDGS() as ddgs:
            # max_results=3 keeps the context window clean for the AI
            results = ddgs.text(query, max_results=3)
            for r in results:
                search_results.append(f"Source: {r['title']}\nSnippet: {r['body']}")

        if not search_results:
            return "No search results were found for that specific query."

        # Join results with a clear separator
        return "\n---\n".join(search_results)

    except Exception as e:
        print(f"SEARCH ERROR: {str(e)}")
        return f"The search tool encountered an error: {str(e)}. Please try again with different keywords."

def check_shipping_status(order_id: str):
    return f"Order {order_id} is currently being processed by the carrier."
