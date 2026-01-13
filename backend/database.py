import sqlite3

def get_db_connection():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Inventory Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            name TEXT PRIMARY KEY,
            price REAL NOT NULL,
            quantity INTEGER DEFAULT 1
        )
    ''')
    
    # 2. Work Tickets Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. Reminders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            remind_at TEXT,
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database Initialized: Inventory, Tickets, and Reminders ready.")
