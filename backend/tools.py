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
        return f"Successfully added {name} at ${price}."
    except Exception as e:
        return f"Database error: {str(e)}"

def check_inventory(query: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{query}%",))
    items = cursor.fetchall()
    conn.close()
    if not items: return f"Nothing found for {query}."
    res = "Stock found: "
    for i in items:
        res += f"{i['name']} (${i['price']}). "
    return res

def web_research(query: str):
    try:
        results_list = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=2):
                results_list.append(f"{r['title']}: {r['body'][:100]}")
        return "Web: " + " | ".join(results_list) if results_list else "No web results found."
    except:
        return "Search failed."
