import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_path = Path("backend").absolute()
sys.path.append(str(backend_path))

# Mock environment for settings
os.environ["SECRET_KEY"] = "dummy_secret_for_testing"
db_path = backend_path / "storage" / "edit_ai.db"
# Ensure directory exists
db_path.parent.mkdir(parents=True, exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"

async def verify_credit_ledger():
    print(f"Python Version: {sys.version}")
    try:
        from app.db import SessionLocal
        from app.models import User, CreditLedger
        from sqlalchemy import select
        
        print("Initializing database session...")
        
        async with SessionLocal() as session:
            print("Creating test user...")
            test_email = f"ledger_test_{int(datetime.now().timestamp())}@example.com"
            new_user = User(email=test_email, password_hash="dummy")
            session.add(new_user)
            await session.commit()
            print(f"User created with ID: {new_user.id}")
            
            print("Creating CreditLedger entry...")
            ledger_entry = CreditLedger(
                user_id=new_user.id,
                delta=100,
                balance_after=100,
                reason="Initial deposit",
                source="test_script"
            )
            session.add(ledger_entry)
            await session.commit()
            print(f"Ledger entry created with ID: {ledger_entry.id}")
            
            print("Verifying Ledger entry...")
            stmt = select(CreditLedger).where(CreditLedger.id == ledger_entry.id)
            result = await session.execute(stmt)
            fetched_entry = result.scalar_one()
            
            print(f"Fetched Entry Delta: {fetched_entry.delta}")
            print(f"Fetched Entry Balance After: {fetched_entry.balance_after}")
            print(f"Fetched Entry Source: {fetched_entry.source}")
            
            assert fetched_entry.delta == 100
            assert fetched_entry.balance_after == 100
            assert fetched_entry.source == "test_script"
            
            # Clean up
            print("Cleaning up...")
            await session.delete(fetched_entry)
            await session.delete(new_user)
            await session.commit()
            
        print("SUCCESS: Credit Ledger interactions passed.")
        
    except Exception as e:
        print("\nCRITICAL FAILURE: Interaction failed.")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_credit_ledger())
