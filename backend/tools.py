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
        return f"Confirmed. {name} has been added to stock at ${price}."
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
        return f"Removed {name} from records." if count > 0 else f"Could not find {name}."
    except Exception as e:
        return f"Error removing item: {str(e)}"

def check_inventory(query: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{query}%",))
    items = cursor.fetchall()
    conn.close()
    if not items: return "That item is not in our inventory."
    return "Stock Status: " + ", ".join([f"{i['name']} (${i['price']})" for i in items])

def web_research(query: str):
    """Broad-spectrum search that bypasses common bot blocks."""
    try:
        results = []
        with DDGS() as ddgs:
            # Combining multiple results ensures we always have data for the AI to 'sort'
            for r in ddgs.text(query, max_results=4):
                results.append(f"Source: {r['title']}\nSnippet: {r['body']}")
        return "\n---\n".join(results) if results else "Search returned no data."
    except Exception as e:
        return f"Search error: {str(e)}"
