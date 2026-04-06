import sqlite3
import os

# Ensure folder exists
os.makedirs("data", exist_ok=True)
DB_PATH = "data/plants.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create table with proper fields
c.execute('''
    CREATE TABLE IF NOT EXISTS plants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        photo_path TEXT,
        last_watered DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Optional: Add sample data
c.execute("INSERT OR IGNORE INTO plants (name, description, last_watered) VALUES ('Monstera', 'Loves indirect light', '2026-04-01')")
c.execute("INSERT OR IGNORE INTO plants (name, description, last_watered) VALUES ('Succulent', 'Water sparingly', NULL)")

conn.commit()
conn.close()

print(f"✅ Database created at {DB_PATH}")
print("Table schema:")
conn = sqlite3.connect(DB_PATH)
print(conn.execute("PRAGMA table_info(plants)").fetchall())
conn.close()