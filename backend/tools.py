import sqlite3
from database import get_db_connection
from duckduckgo_search import DDGS

def add_to_inventory(name: str, price: float, quantity: int = 1):
    try:
        # Objective Fix: Force price to float and clean the product name
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
        return f"Confirmed. {clean_name} logged at ${clean_price:.2f}."
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
        return f"Removed {name}." if count > 0 else f"I couldn't find {name}."
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
        res = "Inventory: "
        for i in items:
            res += f"{i['name']} (${i['price']}) Qty: {i['quantity']}. "
        return res
    except Exception as e:
        return f"DB Error: {str(e)}"

def web_research(query: str):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                results.append(f"Source: {r['title']}\nSnippet: {r['body']}")
        return "\n---\n".join(results) if results else "No online data found."
    except Exception as e:
        return f"Search Error: {str(e)}"
