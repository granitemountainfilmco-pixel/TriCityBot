import sqlite3

DB_NAME = "shop.db"

def init_db():
    """Initializes the database with the inventory table."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price REAL,
            quantity INTEGER,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

def get_db_connection():
    """Returns a connection to the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
