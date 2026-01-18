import sqlite3

conn = sqlite3.connect("auth.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users)")
print(cursor.fetchall())
