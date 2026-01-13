from database import get_db_connection

def add_to_inventory(name: str, price: str, quantity: int = 1):
    try:
        # Objective Fix: Remove commas, dollar signs, and spaces from price
        clean_p = str(price).replace(",", "").replace("$", "").strip()
        final_price = float(clean_p)
        
        # Standardize name: Remove "ADD" or "CHECK" if the AI accidentally left it in
        clean_name = str(name).upper().replace("ADD ", "").replace("CHECK ", "").strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (name, price, quantity) 
            VALUES (?, ?, ?) 
            ON CONFLICT(name) DO UPDATE SET quantity = quantity + ?, price = ?
        """, (clean_name, final_price, quantity, quantity, final_price))
        conn.commit()
        conn.close()
        return f"Confirmed: {clean_name} added at ${final_price}."
    except Exception as e:
        return f"Price error: Could not parse '{price}' as a number."

def check_inventory(query: str):
    # Standardize the search term
    search_term = str(query).upper().replace("CHECK ", "").replace("INVENTORY ", "").strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{search_term}%",))
    items = cursor.fetchall()
    conn.close()
    
    if not items: return f"I couldn't find {search_term} in the records."
    return "Stock: " + ", ".join([f"{i['name']} (${i['price']})" for i in items])

def remove_from_inventory(name: str):
    clean_name = str(name).upper().replace("REMOVE ", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name LIKE ?", (f"%{clean_name}%",))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return f"Removed {clean_name}." if count > 0 else f"Failed to find {clean_name}."

def web_research(query: str):
    from googlesearch import search as gsearch
    try:
        results = [f"Title: {r.title}\nInfo: {r.description}" for r in gsearch(query, num_results=3, advanced=True)]
        return "\n---\n".join(results) if results else "No data."
    except: return "Search blocked."
