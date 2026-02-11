from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
from .config import settings

def hash_password(password: str) -> str:
    # Explicitly truncate to 71 bytes to ensure compatibility 
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 71:
        # Use 71 bytes to be safe (bcrypt restriction is usually 72)
        password_bytes = password_bytes[:71]
    
    # Generate salt and hash
    # rounds=12 matches our previous passlib config
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    # Explicitly truncate to 71 bytes to match the hash logic
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 71:
        password_bytes = password_bytes[:71]
        
    try:
        # bcrypt.checkpw requires bytes
        return bcrypt.checkpw(password_bytes, password_hash.encode('utf-8'))
    except Exception as e:
        # Handle invalid hash formats or other errors gracefully
        print(f"DEBUG: verify_password failed: {e}")
        return False


def generate_access_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=settings.token_expiry_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
