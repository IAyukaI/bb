from asyncio import wait_for, timeout

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QPushButton, QLineEdit, QListWidgetItem, QScrollArea, QMessageBox, QSpinBox, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QPixmap, Qt
from app.db.db_api import get_all_products, get_user_by_username, add_sale
import os

import time

class MainWindow(QMainWindow):
    def __init__(self, user):
        self.user = user
        super().__init__()

        if self.user.role == "admin":
            self.setWindowTitle("Niezamykające sie okienko")
            self.handle_admin()
        else:
            self.setWindowTitle("Piekarnia - Panel główny")
            self.handle_user()

    def handle_user(self):
        # Central widget i główny layout
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # --- Menu u góry ---
        menu_layout = QHBoxLayout()
        # Lewy przycisk (litera "O")
        self.menu_button = QPushButton("Wyloguj")
        self.menu_button.setFixedWidth(100)
        self.menu_button.clicked.connect(self.logout)

        menu_layout.addWidget(self.menu_button, alignment=Qt.AlignLeft)

        # Rozciągliwa przestrzeń między lewym i prawym elementem menu
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        menu_layout.addItem(spacer)

        # Prawa nazwa użytkownika
        username_label = QLabel(f"Użytkownik: {self.user.username}")
        menu_layout.addWidget(username_label, alignment=Qt.AlignRight)

        central_layout.addLayout(menu_layout)

        # --- Główny obszar z produktami i koszykiem ---
        main_layout = QHBoxLayout()

        # Lewy panel: lista produktów w scrollu
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(500)

        # ScrollArea do produktów
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll_content.setLayout(self.scroll_layout)
        scroll.setWidget(scroll_content)

        left_layout.addWidget(scroll)

        main_layout.addWidget(left_widget)

        # Prawy panel: koszyk
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        right_widget.setFixedWidth(300)

        right_layout.addWidget(QLabel("Koszyk:"))
        self.cart_list_widget = QListWidget()
        right_layout.addWidget(self.cart_list_widget)

        # Przycisk zatwierdzenia zakupów
        self.checkout_btn = QPushButton("Kup wybrane")
        self.checkout_btn.clicked.connect(self.checkout)
        right_layout.addWidget(self.checkout_btn)

        main_layout.addWidget(right_widget)

        central_layout.addLayout(main_layout)

        self.cart = []
        self.products = get_all_products()
        self.refresh_products()

    def logout(self):
        from app.ui.login_window import LoginWindow
        self.login_win = LoginWindow()
        self.login_win.show()
        self.close()

    def refresh_products(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget_to_remove = self.scroll_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

        # Mapowanie nazw produktów na konkretne obrazki w katalogu resources
        base_dir = os.path.join(os.path.dirname(__file__), "resources")
        image_map = {
            "Rogalik": "rogalik.jpg",
            "Bagietka": "bagietka.jpg",
            "Bułka kajzerka": "bulka-kajzerka.jpg",
            "Chleb pszenny": "chleb-pszenny.jpg",
            "Chleb razowy": "chleb-razowy.jpg",
            "Ciasto drożdżowe": "ciasto-drozdzowe.jpg",
        }
        default_image = os.path.join(base_dir, "250.png")

        # Dodaj produkty jako widgety
        for product in self.products:
            product_widget = QFrame()
            product_widget.setFrameShape(QFrame.Box)
            product_layout = QHBoxLayout()
            product_widget.setLayout(product_layout)

            # Obrazek po lewej – spróbuj dobrać zdjęcie po nazwie produktu
            img_file = image_map.get(product.name, "250.png")
            img_path = os.path.join(base_dir, img_file)
            if not os.path.exists(img_path):
                img_path = default_image

            pixmap = QPixmap(img_path)
            img_label = QLabel()
            img_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            product_layout.addWidget(img_label)

            # Po prawej nazwa i opis + formularz wyboru ilości i dodania
            right_layout = QVBoxLayout()
            name_label = QLabel(f"{product.name}")
            name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            right_layout.addWidget(name_label)

            desc_label = QLabel("Opis produktu tutaj.")
            desc_label.setWordWrap(True)
            right_layout.addWidget(desc_label)

            # Wybór ilości i przycisk dodaj
            controls_layout = QHBoxLayout()
            quantity_spin = QSpinBox()
            quantity_spin.setMinimum(1)
            quantity_spin.setMaximum(100)
            controls_layout.addWidget(QLabel("Ilość:"))
            controls_layout.addWidget(quantity_spin)

            add_btn = QPushButton("Dodaj")
            controls_layout.addWidget(add_btn)

            right_layout.addLayout(controls_layout)
            product_layout.addLayout(right_layout)

            self.scroll_layout.addWidget(product_widget)

            # Podpięcie funkcji do przycisku dodaj z zachowaniem odniesienia do produktu i pola ilości
            add_btn.clicked.connect(lambda checked=False, p=product, spin=quantity_spin: self.add_to_cart(p, spin.value()))

        self.scroll_layout.addStretch(1)
        self.update_cart()

        if self.user.role == "admin":
            self.close()

    def add_to_cart(self, product, quantity):
        # Sprawdź czy produkt jest już w koszyku, jeśli tak zwiększ ilość
        for item in self.cart:
            if item["product"].id == product.id:
                item["quantity"] += quantity
                break
        else:
            self.cart.append({"product": product, "quantity": quantity})

        self.update_cart()

    def update_cart(self):
        self.cart_list_widget.clear()
        for i, item in enumerate(self.cart):
            product = item["product"]
            qty = item["quantity"]
            list_widget_item = QListWidgetItem(f"{product.name} - {qty} szt. - {round(product.price * qty, 2)} zł")
            self.cart_list_widget.addItem(list_widget_item)
        # Można rozbudować koszyk o obsługę usuwania elementów (np. po kliknięciu)

    def checkout(self):
        if not self.cart:
            QMessageBox.information(self, "Koszyk pusty", "Dodaj produkty do koszyka przed zakupem.")
            return

        if self.user.role == "guest" or self.user.id is None:
            guest_user = get_user_by_username("guest")
            if not guest_user:
                QMessageBox.warning(self, "Błąd", "Brak konta gościa w bazie.")
                return

            def payment_success(card_number):
                for item in self.cart:
                    add_sale(item["product"].id, guest_user.id, item["quantity"])
                QMessageBox.information(self, "Zakup", "Zakup został zarejestrowany dla gościa.")
                self.cart.clear()
                self.update_cart()

            from app.ui.card_payment_window import CardPaymentWindow
            self.card_payment_win = CardPaymentWindow(self.cart, payment_success)
            self.card_payment_win.show()
        else:
            # Sprawdzenie, czy użytkownik MA podaną kartę kredytową
            if not getattr(self.user, "credit_card", None):
                # Jeśli nie ma karty – otwórz okno z prośbą o jej podanie
                from app.ui.card_payment_window import CardPaymentWindow

                def card_entered(card_number):
                    # Tu możesz zapisać numer karty do użytkownika w bazie, jeśli chcesz!
                    # Np. wywołaj funkcję update_user_credit_card(self.user.id, card_number)
                    self.user.credit_card = card_number  # możesz to zrobić, jeśli obiekt użytkownika w pamięci ma taką właściwość
                    self.cart.clear()
                    self.update_cart()

                self.card_payment_win = CardPaymentWindow(self.cart, card_entered)
                self.card_payment_win.show()
                return  # przerywamy, nie rejestrujemy sprzedaży, dopiero po wpisaniu karty!

            # Jeśli karta już podana, wykonaj zakup
            sales_summary = {}
            for item in self.cart:
                p = item["product"]
                cnt = item["quantity"]
                sales_summary[p.id] = sales_summary.get(p.id, 0) + cnt

            for product_id, count in sales_summary.items():
                add_sale(product_id, self.user.id, count)

            QMessageBox.information(self, "Zakup", "Zakup został zarejestrowany.")
            self.cart.clear()
            self.update_cart()

    # === Widok administratora ===
    def handle_admin(self):
        from app.admin.users_window import UsersWindow
        self.main_win = UsersWindow()
        self.main_win.show()
        self.close()

class CardPaymentWindow(QWidget):
    def __init__(self, cart, on_card_entered):
        super().__init__()
        self.cart = cart
        self.on_card_entered = on_card_entered
        self.setWindowTitle("Podaj dane karty kredytowej")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Wprowadź numer karty kredytowej:"))
        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText("Numer karty")
        layout.addWidget(self.card_input)

    def handle_payment(self):
        card_number = self.card_input.text().strip()
        if not card_number:
            QMessageBox.warning(self, "Błąd", "Podaj numer karty.")
            return
        self.on_card_entered(card_number)
        self.close()

