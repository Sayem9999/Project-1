import psutil
import time

def test_psutil():
    print("--- Testing psutil ---")
    start = time.perf_counter()
    try:
        print("Iterating processes...")
        count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            count += 1
            if count % 50 == 0:
                print(f"Checked {count} processes...")
        
        print(f"Total processes: {count}")
        
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        print(f"CPU: {cpu}%")
        print(f"Mem: {mem.percent}%")
        
        print(f"Time taken: {time.perf_counter() - start:.2f}s")
        print("psutil test OK")
    except Exception as e:
        print(f"psutil error: {e}")

if __name__ == "__main__":
    test_psutil()
