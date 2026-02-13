import sqlite3
import json
from pathlib import Path

db_path = Path("backend/storage/edit_ai.db")
if not db_path.exists():
    db_path = Path("storage/edit_ai.db")

if not db_path.exists():
    print(f"Database not found at {db_path.absolute()}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print(f"--- Database Inspection: {db_path.name} ---")

# Last 5 jobs
cursor.execute("SELECT id, status, progress_message, tier, created_at FROM jobs ORDER BY id DESC LIMIT 5")
jobs = cursor.fetchall()
print("\nRecent Jobs:")
for j in jobs:
    print(f"ID: {j[0]} | Status: {j[1]} | Tier: {j[3]} | Msg: {j[2]}")

conn.close()
