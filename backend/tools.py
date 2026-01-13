from database import get_db_connection

def add_to_inventory(name: str, price: float, quantity: int = 1):
    try:
        clean_price, clean_name = float(price), str(name).strip().upper()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (name, price, quantity) 
            VALUES (?, ?, ?) 
            ON CONFLICT(name) DO UPDATE SET quantity = quantity + ?, price = ?
        """, (clean_name, clean_price, quantity, quantity, clean_price))
        conn.commit()
        conn.close()
        return f"Added {clean_name} at ${clean_price}."
    except Exception as e: return f"Error: {str(e)}"

def check_inventory(query: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{query}%",))
    items = cursor.fetchall()
    conn.close()
    if not items: return f"No {query} in stock."
    return "Inventory: " + ", ".join([f"{i['name']} (${i['price']})" for i in items])

def remove_from_inventory(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name LIKE ?", (f"%{name}%",))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return f"Removed {name}." if count > 0 else "Item not found."

def web_research(query: str):
    from googlesearch import search as gsearch
    try:
        results = [f"Title: {r.title}\nInfo: {r.description}" for r in gsearch(query, num_results=3, advanced=True)]
        return "\n---\n".join(results) if results else "No data."
    except: return "Search blocked."
