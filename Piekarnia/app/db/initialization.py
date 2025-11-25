# app/db/initialization.py
from app.db.models import Base
from app.db.database import engine
from app.auth.auth_utils import hash_password
from app.db.db_api import get_user_by_username, create_user

def init_db():
    Base.metadata.create_all(bind=engine)

def init_sample_data():
    from app.db.db_api import add_product, get_all_products
    if not get_all_products():
        add_product("Chleb pszenny", 4.00)
        add_product("Bułka kajzerka", 1.20)
        add_product("Rogalik", 2.50)
        add_product("Bagietka", 3.50)
        add_product("Chleb razowy", 5.00)
        add_product("Ciasto drożdżowe", 10.00)

def create_default_admin():
    if not get_user_by_username("a"):
        create_user(
            username="a",
            password_hash=hash_password("a"),
            role="admin",
            email="admin2@example.com",      # konieczne!
            credit_card=None                # opcjonalne
        )

def create_guest_user():
    # Sprawdź, czy istnieje
    if not get_user_by_username("guest"):
        create_user("guest", hash_password("guest123"), role="guest", email="guest@example.com")
