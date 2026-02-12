import sqlite3
import time

def test_db():
    print("--- Testing DB responsiveness ---")
    start = time.perf_counter()
    try:
        # Connect to the SQLite DB directly (sync)
        conn = sqlite3.connect("storage/edit_ai.db", timeout=5.0)
        cursor = conn.cursor()
        print("Querying users...")
        cursor.execute("SELECT COUNT(*) FROM users")
        res = cursor.fetchone()
        print(f"User count: {res[0]}")
        
        print("Querying jobs...")
        cursor.execute("SELECT COUNT(*) FROM jobs")
        res = cursor.fetchone()
        print(f"Job count: {res[0]}")
        
        conn.close()
        print(f"DB test OK ({time.perf_counter() - start:.2f}s)")
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    test_db()
