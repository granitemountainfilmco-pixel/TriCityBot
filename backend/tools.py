from database import get_db_connection
from duckduckgo_search import DDGS

# --- INVENTORY TOOLS ---
def add_to_inventory(name: str, price: float, quantity: int = 1, notes: str = ""):
    """Adds an item to inventory. Updates quantity if it exists."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventory (name, price, quantity, notes) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET quantity = quantity + ?",
            (name, price, quantity, notes, quantity)
        )
        conn.commit()
        conn.close()
        return f"✅ Success: Added {quantity}x {name} at ${price}."
    except Exception as e:
        return f"❌ Error adding item: {str(e)}"

def remove_from_inventory(name: str):
    """Removes an item completely from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ?", (name,))
    if cursor.rowcount > 0:
        conn.commit()
        msg = f"🗑️ Removed {name} from inventory."
    else:
        msg = f"⚠️ Item '{name}' not found."
    conn.close()
    return msg

def check_inventory(query: str):
    """Searches for items by name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{query}%",))
    items = cursor.fetchall()
    conn.close()
    
    if not items:
        return "⚠️ No items found matching that name."
    
    response = "📦 **Inventory Search:**\n"
    for item in items:
        response += f"- **{item['name']}**: ${item['price']} (Qty: {item['quantity']}) | *{item['notes']}*\n"
    return response

# --- RESEARCH TOOL ---
def web_research(query: str):
    """Searches the web using DuckDuckGo (No API Key needed)."""
    try:
        print(f"🔎 Researching: {query}")
        results = DDGS().text(query, max_results=2)
        if not results:
            return "No results found."
        
        summary = "🌐 **Web Search Results:**\n"
        for res in results:
            summary += f"- [{res['title']}]({res['href']}): {res['body'][:200]}...\n"
        return summary
    except Exception as e:
        return f"Research failed: {e}"

# --- STUBS ---
def check_shipping_status(order_id: str):
    return f"🚚 [MOCK] Order #{order_id} is 'Out for Delivery'."
