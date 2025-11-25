from app.db.database import SessionLocal
from app.db.models import User

def get_all_users():
    with SessionLocal() as session:
        return session.query(User).all()

def delete_user(user_id):
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
            return True
        return False

def edit_user(user_id, new_username, new_email):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        # Sprawdź, czy nowy login lub email nie są już zajęte przez innego użytkownika
        existing_user = db.query(User).filter(User.username == new_username, User.id != user_id).first()
        if existing_user:
            return False  # login już istnieje dla innego użytkownika
        existing_email = db.query(User).filter(User.email == new_email, User.id != user_id).first()
        if existing_email:
            return False  # email już istnieje dla innego użytkownika

        user.username = new_username
        user.email = new_email
        db.commit()
        return True

def change_user_role(user_id, new_role):
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.role = new_role
            db.commit()
            return True
        return False
