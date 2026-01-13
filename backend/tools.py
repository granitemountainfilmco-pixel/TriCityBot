from database import get_db_connection
from duckduckgo_search import DDGS

def add_to_inventory(name: str, price: str, quantity: int = 1):
    try:
        # Clean the input
        clean_name = str(name).upper().replace("ADD ", "").strip()
        clean_price = float(str(price).replace("$", "").replace(",", ""))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (name, price, quantity) 
            VALUES (?, ?, ?) 
            ON CONFLICT(name) DO UPDATE SET quantity = quantity + ?, price = ?
        """, (clean_name, clean_price, quantity, quantity, clean_price))
        conn.commit()
        conn.close()
        return f"Logged: {clean_name} @ ${clean_price}."
    except:
        return "Failed to parse name or price."

def check_inventory(query: str):
    # Strip common filler
    term = str(query).upper().replace("CHECK ", "").replace("INVENTORY ", "").replace("FOR ", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fuzzy match: Find "RTX 5090" even if query is "RTX5090"
    fuzzy = term.replace("RTX", "RTX%")
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{fuzzy}%",))
    items = cursor.fetchall()
    conn.close()
    if not items: return f"Nothing found for {term}."
    return "Stock: " + ", ".join([f"{i['name']} (${i['price']})" for i in items])

def remove_from_inventory(name: str):
    clean = str(name).upper().replace("REMOVE ", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name LIKE ?", (f"%{clean}%",))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return f"Deleted {clean}." if count > 0 else "Not found."

def web_research(query: str):
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, region='wt-wt', safesearch='off'):
                results.append(f"{r['title']}: {r['body']}")
                if len(results) >= 2: break
        return "\n".join(results) if results else "No data."
    except:
        return "Web search unavailable."
