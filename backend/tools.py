import sqlite3
from tavily import TavilyClient

# --- CONFIG ---
TAVILY_API_KEY = "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"
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def get_db_connection():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- INVENTORY TOOLS ---

def add_to_inventory(name: str, price: str, quantity: int = 1):
    try:
        clean_name = str(name).upper().strip()
        clean_price = float(str(price).replace("$", "").replace(",", "").strip())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (name, price, quantity) VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET 
                quantity = quantity + EXCLUDED.quantity, 
                price = EXCLUDED.price
        """, (clean_name, clean_price, quantity))
        conn.commit()
        conn.close()
        return f"Logged: {clean_name} at ${clean_price:,.2f} (qty: {quantity})."
    except Exception as e:
        print(f"DB Error: {e}")
        return f"Error adding item: {str(e)}"

def remove_from_inventory(name: str):
    try:
        clean_name = str(name).upper().strip()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE name = ?", (clean_name,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return f"Removed {clean_name} from inventory." if success else f"Item '{clean_name}' not found."
    except Exception as e:
        return f"Error removing item: {str(e)}"

def check_inventory(term: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    fuzzy = f"%{term.upper().replace(' ', '%')}%"
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (fuzzy,))
    items = cursor.fetchall()
    conn.close()
    if not items: return f"No local stock found for '{term}'."
    return "Inventory Match:\n" + "\n".join([f"- {i['name']}: ${i['price']:,.2f} (x{i['quantity']})" for i in items])

def list_inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    conn.close()
    if not items: return "The inventory is currently empty."
    return "Full Stock List:\n" + "\n".join([f"- {i['name']}: ${i['price']:,.2f} (x{i['quantity']})" for i in items])

# --- WORK TICKET & REMINDER TOOLS ---

def create_ticket(description: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tickets (description) VALUES (?)", (description,))
    conn.commit()
    conn.close()
    return f"Work Ticket Created: {description}"

def list_tickets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description FROM tickets WHERE status = 'OPEN'")
    items = cursor.fetchall()
    conn.close()
    if not items: return "No open work tickets."
    return "Open Work Tickets:\n" + "\n".join([f"#{i['id']}: {i['description']}" for i in items])

def create_reminder(message: str, time_str: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (message, remind_at) VALUES (?, ?)", (message, time_str))
    conn.commit()
    conn.close()
    return f"Reminder Set: '{message}' for {time_str}."

# --- RESEARCH TOOL ---

def web_research(query: str):
    try:
        response = tavily.search(query=query, search_depth="advanced", max_results=3)
        return "\n".join([f"Source: {r['url']} - {r['content']}" for r in response['results']])
    except Exception as e:
        return f"Research failed: {str(e)}"
