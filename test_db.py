import sqlite3
DB_PATH = "data/plants.db"
conn = sqlite3.connect(DB_PATH)
plants = conn.execute("SELECT * FROM plants").fetchall()
print("Plants:", plants)
conn.close()