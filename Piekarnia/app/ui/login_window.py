from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from app.auth.auth_service import login_user


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logowanie")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("LOGOWANIE"))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Login")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Hasło")
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Zaloguj")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        register_btn = QPushButton("Zarejestruj się")
        register_btn.clicked.connect(self.open_registration)
        layout.addWidget(register_btn)

        guest_btn = QPushButton("Kontynuuj jako gość")
        guest_btn.clicked.connect(self.continue_as_guest)
        layout.addWidget(guest_btn)

        self.setLayout(layout)

    def handle_login(self):
        user = login_user(self.username_input.text(), self.password_input.text())
        if user:
            # Jeśli zalogowany użytkownik jest administratorem, od razu otwórz panel admina,
            # pomijając główne okno klienta.
            if getattr(user, "role", None) == "admin":
                from app.admin.users_window import UsersWindow
                self.admin_win = UsersWindow()
                self.admin_win.show()
                self.close()
                return

            from app.ui.main_window import MainWindow
            self.main_win = MainWindow(user)
            self.main_win.show()
            self.close()
        else:
            QMessageBox.warning(self, "Błąd", "Nieprawidłowe dane logowania.")

    def open_registration(self):
        from app.ui.registration_window import RegistrationWindow
        self.reg_win = RegistrationWindow()
        self.reg_win.show()

    def continue_as_guest(self):
        from app.db.db_api import get_user_by_username
        from app.ui.main_window import MainWindow

        guest_user = get_user_by_username("guest")
        if not guest_user:
            QMessageBox.warning(self, "Błąd", "Brak konta gościa w bazie.")
            return

        self.main_win = MainWindow(guest_user)
        self.main_win.show()
        self.close()
