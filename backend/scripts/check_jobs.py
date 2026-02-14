import sqlite3
import os

db_path = "storage/edit_ai.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, status, progress_message, output_path FROM jobs ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]} | Status: {row[1]} | Message: {row[2]} | Path: {row[3]}")
    conn.close()
else:
    print("DB not found")
