from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from app.db.db_api import get_all_products
import os

class ProductsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Produkty")
        layout = QVBoxLayout()

        products = get_all_products()
        if not products:
            layout.addWidget(QLabel("Brak produktów w bazie"))
        else:
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

            for p in products:
                row = QWidget()
                row_layout = QHBoxLayout()
                row.setLayout(row_layout)

                img_file = image_map.get(p.name, "250.png")
                img_path = os.path.join(base_dir, img_file)
                if not os.path.exists(img_path):
                    img_path = default_image

                pixmap = QPixmap(img_path)
                img_label = QLabel()
                img_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                row_layout.addWidget(img_label)

                text = QLabel(f"{p.name} - {p.price} zł")
                text.setStyleSheet("font-size: 14px; font-weight: bold;")
                row_layout.addWidget(text)

                layout.addWidget(row)

        layout.addStretch(1)
        self.setLayout(layout)

    def add_new_product(name: str, price: float):
        from app.db.db_api import add_product
        add_product(name, price)
        # Odśwież listę produktów w GUI
