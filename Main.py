
import tkinter as tk
import Db 
from GUI import InvoiceApp  
Db.create_database()

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()
