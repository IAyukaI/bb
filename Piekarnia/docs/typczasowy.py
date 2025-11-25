import os
from app.db.database import engine, Base

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
if os.path.exists(db_path):
    os.remove(db_path)

Base.metadata.create_all(bind=engine)
print("Baza danych została utworzona od nowa.")