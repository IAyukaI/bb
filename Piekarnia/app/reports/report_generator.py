# app/reports/report_generator.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_report(filename, sales):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "Raport sprzedaży")
    y = 700
    for sale in sales:
        c.drawString(100, y, f"{sale.product.name} x {sale.quantity} - {sale.user.username}")
        y -= 20
    c.save()
