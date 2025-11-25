from app.db.db_api import get_user_by_username, create_user, get_user_by_email
from app.auth.auth_utils import hash_password, verify_password

def login_user(username, password):
    user = get_user_by_username(username)
    if user and verify_password(password, user.password_hash):
        return user
    return None

def register_user(username, password, email, credit_card):
    if get_user_by_username(username):
        return False, "Użytkownik już istnieje"
    if get_user_by_email(email):
        return False, "Email już istnieje"
    if not email:
        return False, "Email jest wymagany"
    password_hashed = hash_password(password)
    create_user(username, password_hashed, role="user", email=email, credit_card=credit_card)
    return True, "Zarejestrowano pomyślnie"



