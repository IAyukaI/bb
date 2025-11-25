from PySide6.QtWidgets import QApplication
from app.ui.login_window import LoginWindow
from app.db.initialization import init_db, init_sample_data, create_default_admin, create_guest_user
import os

def main():
    init_db()
    init_sample_data()
    (create_default_admin
     ())
    (create_guest_user
     ())
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # na pewno działasz w katalogu app/
    app = QApplication([])
    with open("ui/resources/style.qss", "r") as f:
        app.setStyleSheet(f.read())
    login = LoginWindow()
    login.show()
    app.exec()

if __name__ == "__main__":
    main()
