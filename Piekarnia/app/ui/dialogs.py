# app/ui/dialogs.py

from PySide6.QtWidgets import QMessageBox

def show_info(parent, text):
    QMessageBox.information(parent, "Informacja", text)

def show_error(parent, text):
    QMessageBox.critical(parent, "Błąd", text)
