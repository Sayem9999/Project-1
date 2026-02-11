from backend.app.security import hash_password, verify_password

def test_auth():
    print("--- Testing Auth Logic ---")
    
    # Case 1: Normal Password
    pw = "securepassword123"
    print(f"Testing normal password ('{pw}')...")
    hashed = hash_password(pw)
    print(f"Hash generated: {hashed[:10]}...")
    assert verify_password(pw, hashed) == True
    print("Normal password verified.")

    # Case 2: Long Password (>72 bytes)
    long_pw = "a" * 80
    print(f"Testing long password ({len(long_pw)} chars)...")
    
    try:
        # Should NOT raise ValueError anymore, should strictly truncate
        hashed_long = hash_password(long_pw)
        print(f"hash_password succeeded with truncated logic. Hash: {hashed_long[:10]}...")
    except ValueError as e:
        print(f"Failed: hash_password raised ValueError: {e}")

    # Case 3: Verify Long Password against its own hash
    # (Should return True due to truncation match)
    print("Testing verify_password with long input...")
    try:
        result = verify_password(long_pw, hashed_long)
        assert result == True
        print("verify_password correctly returned True (truncation match)")
    except Exception as e:
        print(f"verify_password failed: {e}")

if __name__ == "__main__":
    test_auth()
