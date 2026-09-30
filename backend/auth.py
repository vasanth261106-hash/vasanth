import base64, hashlib, hmac, os, secrets
from fastapi import Request
from .database import connect, now

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 180_000)
    return base64.b64encode(salt + digest).decode()

def verify_password(password: str, stored: str) -> bool:
    try:
        raw = base64.b64decode(stored.encode())
        salt, digest = raw[:16], raw[16:]
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 180_000)
        return hmac.compare_digest(digest, check)
    except Exception: return False

def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    conn = connect(); conn.execute("INSERT INTO sessions VALUES (?,?,?)", (token,user_id,now())); conn.commit(); conn.close()
    return token

def get_user(request: Request):
    token = request.cookies.get("pocketsmart_session")
    if not token: return None
    conn = connect(); row = conn.execute("SELECT u.* FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token=?", (token,)).fetchone(); conn.close()
    return dict(row) if row else None

def logout(token: str | None):
    if not token: return
    conn=connect(); conn.execute("DELETE FROM sessions WHERE token=?", (token,)); conn.commit(); conn.close()

def make_jwt_like(user_id: int, secret: str) -> str:
    # Lightweight HS256-compatible token for the demo project's /token endpoint.
    header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode((f'{{"sub":{user_id}}}').encode()).rstrip(b"=").decode()
    sig = hmac.new(secret.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    return f"{header}.{payload}.{base64.urlsafe_b64encode(sig).rstrip(b'=').decode()}"
