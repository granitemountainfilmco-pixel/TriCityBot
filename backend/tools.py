import os
import sqlite3
from database import get_db_connection
from tavily import TavilyClient

TAVILY_API_KEY = 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
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# --- INVENTORY ---
def add_to_inventory(name, price, quantity=1):
    try:
        name = name.upper().replace("NONE", "").strip()
        if not name: return "Error: No item name provided."
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (name, price, quantity) VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET 
                quantity = inventory.quantity + EXCLUDED.quantity, 
                price = EXCLUDED.price
        """, (name, float(price), int(quantity)))
        conn.commit()
        conn.close()
        return f"Successfully added {quantity}x {name} at ${float(price):,.2f}."
    except Exception as e:
        return f"Add Error: {str(e)}"

def check_inventory(term):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"%{term.upper().strip()}%"
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (query,))
    items = cursor.fetchall()
    conn.close()
    if not items: return f"No stock found matching '{term}'."
    return "Stock results:\n" + "\n".join([f"- {i['name']}: ${i['price']:,.2f} (x{i['quantity']})" for i in items])

def list_inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    conn.close()
    if not items: return "The inventory is currently empty."
    return "Full Stock List:\n" + "\n".join([f"- {i['name']}: ${i['price']:,.2f} (x{i['quantity']})" for i in items])

def remove_from_inventory(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Using UPPER for consistency
    cursor.execute("DELETE FROM inventory WHERE UPPER(name) = ?", (name.upper().strip(),))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return f"Removed {name.upper()}." if success else f"Could not find {name} to remove."

# --- WORK TICKETS ---
def create_ticket(desc):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tickets (description, status) VALUES (?, 'OPEN')", (desc,))
    conn.commit()
    conn.close()
    return f"Ticket Created: {desc}"

def list_tickets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description FROM tickets WHERE status = 'OPEN'")
    items = cursor.fetchall()
    conn.close()
    if not items: return "No open work tickets."
    return "To-Do List:\n" + "\n".join([f"#{i['id']}: {i['description']}" for i in items])

def delete_ticket(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return f"Ticket #{ticket_id} closed/deleted." if success else f"Ticket #{ticket_id} not found."

# --- REMINDERS ---
def create_reminder(msg, time):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (message, remind_at) VALUES (?, ?)", (msg, time))
    conn.commit()
    conn.close()
    return f"Reminder logged: '{msg}' for {time}."

def list_reminders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT message, remind_at FROM reminders ORDER BY remind_at ASC")
    items = cursor.fetchall()
    conn.close()
    if not items: return "No active reminders."
    return "Reminders:\n" + "\n".join([f"- {i['message']} ({i['remind_at']})" for i in items])

def delete_reminder(msg):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fuzzy match for reminders since users rarely type the message exactly
    query = f"%{msg.strip()}%"
    cursor.execute("DELETE FROM reminders WHERE message LIKE ?", (query,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return f"Deleted reminder matching '{msg}'." if success else f"No reminder found matching '{msg}'."

# --- RESEARCH ---
def web_research(query):
    try:
        response = tavily.search(query=query, max_results=3)
        return "\n".join([r['content'] for r in response['results']])
    except:
        return "Search failed."
