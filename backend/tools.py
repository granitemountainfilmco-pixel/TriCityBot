import sqlite3
from database import get_db_connection
from duckduckgo_search import DDGS

def add_to_inventory(name: str, price: float, quantity: int = 1):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventory (name, price, quantity) VALUES (?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET quantity = quantity + ?",
            (name, price, quantity, quantity)
        )
        conn.commit()
        conn.close()
        return f"Confirmed. I've added {name} to the inventory at ${price}."
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
        if count > 0:
            return f"Success. {name} has been removed from the stock records."
        return f"I couldn't find an item named {name} to remove."
    except Exception as e:
        return f"Error removing item: {str(e)}"

def check_inventory(query: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{query}%",))
        items = cursor.fetchall()
        conn.close()
        if not items: return f"We currently don't have {query} in stock."
        res = "Inventory Status: "
        for i in items:
            res += f"{i['name']} is ${i['price']} with {i['quantity']} available. "
        return res
    except Exception as e:
        return f"Database error: {str(e)}"

def web_research(query: str):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=4):
                results.append(f"Title: {r['title']}\nSnippet: {r['body']}")
        return "\n---\n".join(results) if results else "No online data found."
    except Exception as e:
        return f"Research tool failed: {str(e)}"
