from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if len(password.encode('utf-8')) > 72:
        raise ValueError("Password is too long (max 72 characters)")
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    # bcrypt has a 72 byte limit. If the provided password is longer, it cannot match.
    if len(password.encode('utf-8')) > 72:
        return False
    return pwd_context.verify(password, password_hash)


def generate_access_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=settings.token_expiry_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
