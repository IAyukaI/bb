from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QLabel, QPushButton, QMessageBox, QLineEdit, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QSpacerItem, QSizePolicy, QFileDialog
)
from app.admin.admin_service import get_all_users, delete_user, edit_user, change_user_role
from app.db.db_api import get_sales_by_user_id
from app.reports.report_generator import generate_report

print("Uruchamiam panel administratora")


class UsersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel administratora - użytkownicy")

        # Główny layout okna: nagłówek u góry + dwa panele poniżej
        root_layout = QVBoxLayout()

        # Pasek nagłówka z tytułem i przyciskiem "Wyloguj"
        header_layout = QHBoxLayout()
        title_label = QLabel("Panel administratora")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        header_layout.addItem(header_spacer)

        logout_btn = QPushButton("Wyloguj")
        logout_btn.setFixedWidth(100)
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)

        root_layout.addLayout(header_layout)

        # Główny obszar z listą użytkowników i historią zakupów
        main_layout = QHBoxLayout()

        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(1, 1, 1, 1)  # Trochę marginesu w lewym panelu
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(420)  # Zwiększ szerokość panelu użytkowników
        left_widget.setFixedHeight(600)  # Zwiększ szerokość panelu użytkowników
        left_layout.addWidget(QLabel("Użytkownicy:"))

        self.user_list = QListWidget()
        self.user_list.itemClicked.connect(self.show_user_history)
        left_layout.addWidget(self.user_list)
        main_layout.addWidget(left_widget)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Historia zakupów:"))
        self.history_list = QListWidget()
        right_layout.addWidget(self.history_list)

        # Przycisk eksportu raportu PDF dla wybranego użytkownika
        self.export_btn = QPushButton("Eksportuj raport PDF")
        self.export_btn.clicked.connect(self.export_report)
        right_layout.addWidget(self.export_btn)

        main_layout.addLayout(right_layout)

        # Podłącz główny obszar do layoutu root
        root_layout.addLayout(main_layout)
        self.setLayout(root_layout)

        self.users = []
        self.selected_user = None
        self.load_users()

    def load_users(self):
        self.users = get_all_users()
        self.user_list.clear()
        for user in self.users:
            widget = QWidget()
            h_layout = QHBoxLayout()
            h_layout.setSpacing(2)

            info_label = QLabel(f"{user.id} - {user.username} ({user.role})")
            h_layout.addWidget(info_label)

            del_btn = QPushButton("Usuń")
            del_btn.setFixedWidth(60)
            del_btn.clicked.connect(lambda checked, u=user: self.handle_delete(u))
            h_layout.addWidget(del_btn)

            edit_btn = QPushButton("Edytuj")
            edit_btn.setFixedWidth(70)
            edit_btn.clicked.connect(lambda checked, u=user: self.handle_edit(u))
            h_layout.addWidget(edit_btn)

            perm_btn = QPushButton("Rola")
            perm_btn.setFixedWidth(70)
            perm_btn.clicked.connect(lambda checked, u=user: self.handle_role(u))
            h_layout.addWidget(perm_btn)

            widget.setLayout(h_layout)
            item = QListWidgetItem(self.user_list)
            item.setSizeHint(widget.sizeHint())
            item.setData(1000, user)
            self.user_list.addItem(item)
            self.user_list.setItemWidget(item, widget)

        self.history_list.clear()

    def show_user_history(self, item):
        user = item.data(1000)
        if user is None:  # Przypadek kliknięcia w 'spacer'
            return
        self.selected_user = user
        self.history_list.clear()
        sales = get_sales_by_user_id(user.id)
        if not sales:
            self.history_list.addItem("Brak zakupów")
            return
        for sale in sales:
            product_name = getattr(sale.product, "name", "Nieznany produkt")
            quantity = getattr(sale, "quantity", "N/A")
            self.history_list.addItem(f"{product_name}: {quantity}")

    def handle_delete(self, user):
        reply = QMessageBox.question(self, "Usuń użytkownika", f"Czy na pewno chcesz usunąć {user.username}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if delete_user(user.id):
                QMessageBox.information(self, "Usunięto", "Użytkownik został usunięty.")
                self.load_users()
            else:
                QMessageBox.warning(self, "Błąd", "Nie udało się usunąć użytkownika.")

    def handle_edit(self, user):
        dlg = EditUserDialog(user, self)
        if dlg.exec():
            new_name, new_email = dlg.get_data()
            if edit_user(user.id, new_name, new_email):
                QMessageBox.information(self, "Zapisano", "Zmiany zapisane.")
                self.load_users()
            else:
                QMessageBox.warning(self, "Błąd", "Nie udało się zapisać zmian.")

    def handle_role(self, user):
        dlg = RoleDialog(user, self)
        if dlg.exec():
            new_role = dlg.get_role()
            if change_user_role(user.id, new_role):
                QMessageBox.information(self, "Zmieniono", "Rola została zmieniona.")
                self.load_users()
            else:
                QMessageBox.warning(self, "Błąd", "Nie udało się zmienić roli.")

    def logout(self):
        """Wyloguj administratora i wróć do okna logowania."""
        from app.ui.login_window import LoginWindow
        self.login_win = LoginWindow()
        self.login_win.show()
        self.close()

    def export_report(self):
        """Eksportuje raport PDF sprzedaży dla aktualnie wybranego użytkownika."""
        if not getattr(self, "selected_user", None):
            QMessageBox.warning(self, "Brak użytkownika", "Najpierw wybierz użytkownika z listy.")
            return

        user = self.selected_user
        sales = get_sales_by_user_id(user.id)
        if not sales:
            QMessageBox.information(self, "Brak danych", "Wybrany użytkownik nie ma żadnych zakupów do raportu.")
            return

        default_name = f"raport_user_{user.id}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz raport PDF", default_name, "PDF Files (*.pdf)")
        if not file_path:
            return

        try:
            generate_report(file_path, sales)
            QMessageBox.information(self, "Zapisano", f"Raport zapisany jako:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wygenerować raportu:\n{e}")


class EditUserDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edytuj użytkownika")
        self.name_edit = QLineEdit(user.username)
        self.email_edit = QLineEdit(user.email)
        layout = QFormLayout()
        layout.addRow("Login:", self.name_edit)
        layout.addRow("Email:", self.email_edit)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_data(self):
        return self.name_edit.text(), self.email_edit.text()


class RoleDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zmień rolę użytkownika")
        self.box = QComboBox()
        self.box.addItems(['user', 'admin'])
        self.box.setCurrentText(user.role)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Wybierz nową rolę:"))
        layout.addWidget(self.box)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_role(self):
        return self.box.currentText()
