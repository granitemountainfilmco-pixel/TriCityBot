import sqlite3
from tavily import TavilyClient
from database import get_db_connection

TAVILY_API_KEY = "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"
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# --- INVENTORY ---
def add_to_inventory(name: str, price: str, quantity: int = 1):
    try:
        clean_name = str(name).upper().strip()
        clean_price = float(str(price).replace("$", "").replace(",", "").strip())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (name, price, quantity) VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET quantity = quantity + EXCLUDED.quantity, price = EXCLUDED.price
        """, (clean_name, clean_price, quantity))
        conn.commit()
        conn.close()
        return f"Logged: {clean_name} at ${clean_price:,.2f} (qty: {quantity})."
    except Exception as e:
        return f"Error: {str(e)}"

def remove_from_inventory(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ?", (name.upper().strip(),))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return f"Removed {name}." if success else f"Not found: {name}"

def check_inventory(search_term: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fuzzy match: replaces spaces with % for broader search
    fuzzy = f"%{search_term.upper().replace(' ', '%')}%"
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (fuzzy,))
    items = cursor.fetchall()
    conn.close()
    if not items: return f"No local stock found for '{search_term}'."
    return "Stock Found:\n" + "\n".join([f"- {i['name']}: ${i['price']:,.2f} (x{i['quantity']})" for i in items])

def list_inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    conn.close()
    return "Full Stock:\n" + "\n".join([f"- {i['name']}: ${i['price']:,.2f} (x{i['quantity']})" for i in items]) if items else "Inventory empty."

# --- TICKETS & REMINDERS ---
def create_ticket(desc: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tickets (description) VALUES (?)", (desc,))
    conn.commit()
    conn.close()
    return f"Ticket Created: {desc}"

def list_tickets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description FROM tickets WHERE status = 'OPEN'")
    items = cursor.fetchall()
    conn.close()
    return "Tickets:\n" + "\n".join([f"#{i['id']} {i['description']}" for i in items]) if items else "No open tickets."

def create_reminder(msg: str, time: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (message, remind_at) VALUES (?, ?)", (msg, time))
    conn.commit()
    conn.close()
    return f"Reminder: {msg} set for {time}"

def web_research(query: str):
    try:
        res = tavily.search(query=query, max_results=3)
        return "\n".join([r['content'] for r in res['results']])
    except: return "Research unavailable."
