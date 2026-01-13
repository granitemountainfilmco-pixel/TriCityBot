import sqlite3
from googlesearch import search as gsearch

def get_db_connection():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_to_inventory(name: str, price: float, quantity: int = 1):
    try:
        clean_price = float(price)
        clean_name = str(name).strip().upper()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventory (name, price, quantity) VALUES (?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET quantity = quantity + ?, price = ?",
            (clean_name, clean_price, quantity, quantity, clean_price)
        )
        conn.commit()
        conn.close()
        return f"Logged {clean_name} at ${clean_price:.2f}."
    except Exception as e:
        return f"Database error: {str(e)}"

def remove_from_inventory(name: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE name LIKE ?", (f"%{name}%",))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return f"Removed {name}." if count > 0 else f"Could not find {name}."
    except Exception as e:
        return f"Error: {str(e)}"

def check_inventory(query: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{query}%",))
        items = cursor.fetchall()
        conn.close()
        if not items: return f"Nothing found for {query}."
        return "Stock: " + ", ".join([f"{i['name']} (${i['price']}) x{i['quantity']}" for i in items])
    except Exception as e:
        return f"DB Error: {str(e)}"

def web_research(query: str):
    """The 'Better Way': Uses google-search-python for higher reliability."""
    try:
        print(f"Searching web for: {query}")
        results = []
        # num_results=5 provides enough context for the AI summarizer
        for result in gsearch(query, num_results=5, advanced=True):
            results.append(f"Title: {result.title}\nInfo: {result.description}")
        
        return "\n---\n".join(results) if results else "No data found."
    except Exception as e:
        print(f"Search failed: {e}")
        return "The search engine is currently blocking the request."
