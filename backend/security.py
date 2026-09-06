import os, hashlib, hmac, secrets

def hash_password(password):
    salt=secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
    return f"{salt}${digest}"

def verify_password(password, stored):
    try:
        salt,digest=stored.split("$",1)
        check=hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
        return hmac.compare_digest(check,digest)
    except ValueError:
        return False

def make_token(user_id):
    # Lightweight demo token. For production, replace with signed JWT/session storage.
    return f"demo-{user_id}-{secrets.token_urlsafe(24)}"
