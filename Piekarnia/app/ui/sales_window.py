from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton, QMessageBox
from app.db.db_api import get_all_products, add_sale

class SalesWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Rejestracja sprzedaży")
        layout = QVBoxLayout()

        self.product_combo = QComboBox()
        self.products = get_all_products()
        for p in self.products:
            self.product_combo.addItem(f"{p.name} - {p.price} zł", p.id)
        layout.addWidget(QLabel("Wybierz produkt:"))
        layout.addWidget(self.product_combo)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(100)
        layout.addWidget(QLabel("Ilość:"))
        layout.addWidget(self.quantity_spin)

        buy_btn = QPushButton("Kup")
        buy_btn.clicked.connect(self.buy_product)
        layout.addWidget(buy_btn)

        self.setLayout(layout)

    def buy_product(self):
        product_id = self.product_combo.currentData()
        quantity = self.quantity_spin.value()
        add_sale(product_id, self.user.id, quantity)
        QMessageBox.information(self, "Sukces", "Sprzedaż została zarejestrowana!")
