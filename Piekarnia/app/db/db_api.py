from app.db.database import SessionLocal
from app.db.models import User, Product, Sale
from sqlalchemy.orm import joinedload

def get_user_by_username(username):
    with SessionLocal() as db:
        return db.query(User).filter(User.username == username).first()

def get_user_by_email(email):
    with SessionLocal() as db:
        return db.query(User).filter(User.email == email).first()

def create_user(username, password_hash, role="user", email=None, credit_card=None):
    with SessionLocal() as db:
        new_user = User(
            username=username,
            password_hash=password_hash,
            role=role,
            email=email,
            credit_card=credit_card
        )
        db.add(new_user)
        db.commit()

def get_all_users():
    with SessionLocal() as db:
        return db.query(User).all()

def get_all_products():
    with SessionLocal() as session:
        # sesja jest prawidłowo powiązana z engine
        return session.query(Product).all()

def add_product(name, price):
    with SessionLocal() as session:
        product = Product(name=name, price=price)
        session.add(product)
        session.commit()

def get_product_by_id(product_id):
    with SessionLocal() as db:
        return db.query(Product).filter(Product.id == product_id).first()

def update_product(product_id, name=None, price=None):
    with SessionLocal() as db:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            if name:
                product.name = name
            if price is not None:
                product.price = price
            db.commit()
            return True
        return False

def delete_product(product_id):
    with SessionLocal() as db:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            db.delete(product)
            db.commit()
            return True
        return False

def add_sale(product_id, user_id, quantity):
    with SessionLocal() as session:
        sale = Sale(product_id=product_id, user_id=user_id, quantity=quantity)
        session.add(sale)
        session.commit()
def get_sales():
    """Zwraca wszystkie sprzedaże z wstępnie załadowanymi relacjami user i product.

    Dzięki temu obiekty można bezpiecznie wykorzystywać poza sesją (np. w report_generator).
    """
    with SessionLocal() as session:
        return (
            session.query(Sale)
            .options(joinedload(Sale.product), joinedload(Sale.user))
            .all()
        )


def get_sales_by_user_id(user_id):
    """Zwraca sprzedaże danego użytkownika z wstępnie załadowanymi relacjami.

    Ładowanie product i user zapobiega błędom DetachedInstanceError przy generowaniu raportów.
    """
    with SessionLocal() as session:
        return (
            session.query(Sale)
            .options(joinedload(Sale.product), joinedload(Sale.user))
            .filter(Sale.user_id == user_id)
            .all()
        )
