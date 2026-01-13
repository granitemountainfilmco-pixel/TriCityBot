from database import get_db_connection
from googlesearch import search as gsearch

def add_to_inventory(name: str, price: str, quantity: int = 1):
    try:
        # SCRUB: Remove commas, $, and spaces from the price string
        clean_p = str(price).replace(",", "").replace("$", "").strip()
        final_price = float(clean_p)
        
        # SCRUB: Standardize name and remove accidental AI 'action' words
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
        return f"Confirmed: {clean_name} logged at ${final_price}."
    except Exception as e:
        return f"Data Error: Could not process price '{price}'."

def check_inventory(query: str):
    # Fix: Remove common filler but keep the core product name intact
    search_term = str(query).upper()
    for word in ["CHECK", "INVENTORY", "FOR", "SEARCH"]:
        search_term = search_term.replace(word, "")
    search_term = search_term.strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Use a wildcards on BOTH sides and handle potential missing spaces
    # This finds "RTX 5090" even if the user says "RTX5090"
    spaced_term = search_term.replace("RTX", "RTX ")
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ? OR name LIKE ?", 
                   (f"%{search_term}%", f"%{spaced_term}%"))
    
    items = cursor.fetchall()
    conn.close()
    
    if not items: return f"I found nothing for {search_term}."
    return "Stock: " + ", ".join([f"{i['name']} (${i['price']})" for i in items])

def remove_from_inventory(name: str):
    clean_name = str(name).upper().replace("REMOVE ", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name LIKE ?", (f"%{clean_name}%",))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return f"Removed {clean_name}." if count > 0 else f"No item found."

def web_research(query: str):
    try:
        results = [f"Title: {r.title}\nInfo: {r.description}" for r in gsearch(query, num_results=3, advanced=True)]
        return "\n---\n".join(results) if results else "No data."
    except: return "Research blocked by search engine."
