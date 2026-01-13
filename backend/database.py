import sqlite3

def get_db_connection():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            name TEXT PRIMARY KEY,
            price REAL NOT NULL,
            quantity INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()
    print("Database Structured: Table 'inventory' is ready.")
