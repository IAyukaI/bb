from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from app.auth.auth_service import register_user

class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rejestracja nowego użytkownika")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("REJESTRACJA"))

        # Pole loginu (username)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Login")
        layout.addWidget(self.username_input)

        # Pole email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)

        # Pole karta kredytowa (opcjonalne)
        self.credit_card_input = QLineEdit()
        self.credit_card_input.setPlaceholderText("Karta kredytowa (opcjonalne)")
        layout.addWidget(self.credit_card_input)

        # Pole hasła
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Hasło")
        layout.addWidget(self.password_input)

        # Pole potwierdzenia hasła
        self.password_confirm_input = QLineEdit()
        self.password_confirm_input.setEchoMode(QLineEdit.Password)
        self.password_confirm_input.setPlaceholderText("Potwierdź hasło")
        layout.addWidget(self.password_confirm_input)

        register_btn = QPushButton("Zarejestruj")
        register_btn.clicked.connect(self.handle_register)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def handle_register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        credit_card = self.credit_card_input.text().strip()
        if credit_card == "":
            credit_card = None
        password = self.password_input.text()
        password_confirm = self.password_confirm_input.text()

        # Prosta walidacja pól wymaganych
        if not username or not email or not password:
            QMessageBox.warning(self, "Błąd", "Wypełnij wszystkie wymagane pola: login, email i hasło.")
            return

        if password != password_confirm:
            QMessageBox.warning(self, "Błąd", "Hasła nie są takie same.")
            return

        # Możesz tu dodać walidację email i numeru karty jeśli chcesz

        success, msg = register_user(username, password, email, credit_card)
        if success:
            QMessageBox.information(self, "Sukces", "Konto zostało utworzone. Możesz się zalogować.")
            self.close()
        else:
            QMessageBox.warning(self, "Błąd", msg)
