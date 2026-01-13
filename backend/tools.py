from database import get_db_connection
from duckduckgo_search import DDGS

def add_to_inventory(name: str, price: str, quantity: int = 1):
    try:
        clean_p = str(price).replace(",", "").replace("$", "").strip()
        final_price = float(clean_p)
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
    search_term = str(query).upper().replace("CHECK ", "").replace("INVENTORY ", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fuzzy matching handles RTX5090 vs RTX 5090
    spaced_version = search_term.replace("RTX", "RTX ")
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ? OR name LIKE ?", 
                   (f"%{search_term}%", f"%{spaced_version}%"))
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
        print(f"Fetching web data for: {query}")
        results = []
        with DDGS() as ddgs:
            # We fetch 3 results to give the AI context
            for r in ddgs.text(query, region='wt-wt', safesearch='off'):
                results.append(f"Source: {r['title']}\nInfo: {r['body']}")
                if len(results) >= 3: break
        return "\n---\n".join(results) if results else "No data."
    except Exception as e:
        print(f"Search Error: {e}")
        return "The web search tool is temporarily unavailable."
