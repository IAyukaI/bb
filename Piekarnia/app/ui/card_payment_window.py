from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class CardPaymentWindow(QWidget):
    def __init__(self, cart, on_payment_success):
        super().__init__()
        self.cart = cart
        self.on_payment_success = on_payment_success
        self.setWindowTitle("Podaj dane karty kredytowej")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Wprowadź numer karty kredytowej:"))

        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText("Numer karty")
        layout.addWidget(self.card_input)

        pay_btn = QPushButton("Zapłać")
        pay_btn.clicked.connect(self.handle_payment)
        layout.addWidget(pay_btn)

        self.setLayout(layout)

    def handle_payment(self):
        card_number = self.card_input.text().strip()
        if not card_number:
            QMessageBox.warning(self, "Błąd", "Podaj numer karty.")
            return

        # Tu możesz dodać walidację numeru karty (opcjonalne)

        QMessageBox.information(self, "Sukces", "Płatność została zatwierdzona.")
        self.on_payment_success(card_number)

        self.close()
