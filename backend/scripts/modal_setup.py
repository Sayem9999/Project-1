import os
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, env=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def setup_modal():
    print("--- ProEdit Modal GPU Setup ---")
    
    # 1. Check if modal is installed
    try:
        import modal
    except ImportError:
        print("Installing modal client...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "modal"])
        import modal
        
    # 2. Check tokens
    if not os.getenv("MODAL_TOKEN_ID") or not os.getenv("MODAL_TOKEN_SECRET"):
        print("\n[!] ERROR: Modal tokens not found in environment.")
        print("Please run: modal token set")
        print("Or set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET in your terminal.\n")
        return

    # 3. Create Secrets on Modal
    print("Creating R2 secrets on Modal...")
    # These should match your .env values
    # We'll try to read them from .env if possible
    env_vars = {}
    if Path(".env").exists():
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    env_vars[key] = val.strip('"').strip("'")

    r2_keys = ["R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME"]
    missing = [k for k in r2_keys if k not in env_vars]
    
    if missing:
        print(f"Missing R2 keys in .env: {missing}")
        return

    secret_cmd = [
        "modal", "secret", "create", "proedit-r2-secrets",
        f"R2_ACCOUNT_ID={env_vars['R2_ACCOUNT_ID']}",
        f"R2_ACCESS_KEY_ID={env_vars['R2_ACCESS_KEY_ID']}",
        f"R2_SECRET_ACCESS_KEY={env_vars['R2_SECRET_ACCESS_KEY']}",
        f"R2_BUCKET_NAME={env_vars['R2_BUCKET_NAME']}"
    ]
    run_cmd(secret_cmd)

    # 4. Deploy the worker
    print("Deploying worker to Modal cloud...")
    deploy_cmd = ["modal", "deploy", "modal_worker.py"]
    if run_cmd(deploy_cmd):
        print("\n[SUCCESS] Modal Worker is live!")
        print("Your backend will now automatically offload Pro rendering to GPU.")
    else:
        print("\n[FAILED] Deployment failed.")

if __name__ == "__main__":
    # Change to backend dir if needed
    if Path("backend").exists():
        os.chdir("backend")
    setup_modal()
