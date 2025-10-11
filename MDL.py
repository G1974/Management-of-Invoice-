
from datetime import date

class InvoiceModel:
    def __init__(self):
        self.client_id = None
        self.first_name = ""
        self.last_name = ""
        self.phone = ""
        self.postal_code = ""
        self.vat_rate = 0.24  
        self.items = []      
        self.date = date.today()
        self.notes = ""

    def subtotal(self):
        total = 0
        for item in self.items:
            total += item['qty'] * item['price']
        return total

    def vat_amount(self):
        return self.subtotal() * self.vat_rate

    def total(self):
        return self.subtotal() + self.vat_amount()
