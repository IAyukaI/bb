import bcrypt

from app.db.db_api import get_user_by_username


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def login_user(username, password):
    user = get_user_by_username(username)
    if user and verify_password(password, user.password_hash):  # password_hash jest bajtami
        return user
    return None
