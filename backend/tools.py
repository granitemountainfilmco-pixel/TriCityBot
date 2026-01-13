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
        return f"Successfully added {quantity}x {name} at ${price}."
    except Exception as e:
        return f"Error adding to inventory: {str(e)}"

def remove_from_inventory(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ?", (name,))
    rowcount = cursor.rowcount
    conn.commit()
    conn.close()
    return f"Removed {name} from inventory." if rowcount > 0 else f"Item {name} not found."

def check_inventory(query: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{query}%",))
    items = cursor.fetchall()
    conn.close()
    if not items: return "No matching items in stock."
    res = "Inventory found:\n"
    for i in items:
        res += f"- {i['name']}: ${i['price']} (Qty: {i['quantity']})\n"
    return res

def web_research(query: str):
    """Robust web search using DuckDuckGo context manager."""
    try:
        print(f"Searching web for: {query}")
        results_list = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                results_list.append(f"{r['title']}: {r['body'][:150]}")
        
        if not results_list:
            return "Search returned no results. Try simplifying the query."
        return "Web Results:\n" + "\n".join(results_list)
    except Exception as e:
        return f"Search error: {str(e)}"

def check_shipping_status(order_id: str):
    return f"Order {order_id} status: Processing (Mock API)."
