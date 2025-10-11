
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from PDF import export_invoice_pdf 
import Db 

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice App")
        self.invoice_items = []

        self.create_widgets()
        self.refresh_clients()
        self.refresh_invoice_list()

    def create_widgets(self):
        self.root.configure(bg='lightblue')
        mainframe = tk.Frame(self.root, bg='lightblue', padx=8, pady=8)
        mainframe.pack(fill=tk.BOTH, expand=True)
        
        top = tk.Frame(mainframe, bg='lightblue')
        top.pack(fill=tk.X, pady=(0,6))

        ttk.Label(top, text='Client:', background='lightblue').pack(side=tk.LEFT)
        self.client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(top, textvariable=self.client_var, state='readonly')
        self.client_combo.pack(side=tk.LEFT, padx=6)
        tk.Button(top, text='Add Client', bg='gold', fg='black', command=self.add_client_popup).pack(side=tk.LEFT, padx=6)

        ttk.Label(top, text='Date:', background='lightblue').pack(side=tk.LEFT, padx=(12,0))
        self.date_entry = DateEntry(top, width=12)
        self.date_entry.pack(side=tk.LEFT)

        middle_frame = tk.Frame(mainframe, bg='yellow', padx=2, pady=2)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        cols = ("Description", "Qty", "Price", "Total")
        self.tree = ttk.Treeview(middle_frame, columns=cols, show="headings", height=8)
        style = ttk.Style()
        style.configure("Treeview", background="yellow", fieldbackground="yellow", rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.tree.column("Description", anchor="center", width=80, minwidth=250)
        self.tree.column("Qty", anchor="center", width=80)
        self.tree.column("Price", anchor="center", width=80)
        self.tree.column("Total", anchor="center", width=80)

        for c in cols:
            self.tree.heading(c, text=c, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        form = tk.Frame(mainframe, bg='lightblue')
        form.pack(fill=tk.X)

        self.desc = tk.Entry(form, width=40, bg='slate gray')
        self.qty = tk.Entry(form, width=8, bg='slate gray')
        self.price = tk.Entry(form, width=10, bg='slate gray')

        ttk.Label(form, text='Desc', background='lightblue').grid(row=0, column=0)
        self.desc.grid(row=0, column=1)
        ttk.Label(form, text='Qty', background='lightblue').grid(row=0, column=2)
        self.qty.grid(row=0, column=3)
        ttk.Label(form, text='Price', background='lightblue').grid(row=0, column=4)
        self.price.grid(row=0, column=5)

        tk.Button(form, text='Add', bg='orange', fg='black', command=self.add_item).grid(row=0, column=6, padx=6)
        tk.Button(form, text='Remove', bg='red', fg='white', command=self.remove_item).grid(row=0, column=7)

        summary = tk.Frame(mainframe, bg='lightblue')
        summary.pack(fill=tk.X, pady=6)
        self.subtotal_var = tk.StringVar(value='0.00')
        self.total_var = tk.StringVar(value='0.00')
        self.vat_var = tk.DoubleVar(value=24.0)

        ttk.Label(summary, text='Subtotal:', background='lightblue').grid(row=0, column=0)
        ttk.Label(summary, textvariable=self.subtotal_var, background='lightblue').grid(row=0, column=1)
        ttk.Label(summary, text='VAT (%):', background='lightblue').grid(row=0, column=2)
        ttk.Spinbox(summary, from_=0, to=100, textvariable=self.vat_var, width=6, command=self.update_totals).grid(row=0, column=3)
        ttk.Label(summary, text='Total:', background='lightblue').grid(row=0, column=4)
        ttk.Label(summary, textvariable=self.total_var, background='lightblue').grid(row=0, column=5)

        btns = tk.Frame(mainframe, bg='lightblue')
        btns.pack(fill=tk.X, pady=6)
        tk.Button(btns, text='Save Invoice', bg='lightgreen', fg='black', command=self.save_invoice).pack(side=tk.LEFT, padx=4, pady=2)
        tk.Button(btns, text='Export PDF', bg='lightgreen', fg='black', command=self.export_pdf).pack(side=tk.LEFT, padx=4, pady=2)
        tk.Button(btns, text='Refresh', bg='lightgreen', fg='black', command=self.refresh_invoice_list).pack(side=tk.LEFT, padx=4, pady=2)

        self.inv_tree = ttk.Treeview(mainframe, columns=('id','date','client','total'), show='headings', height=6)
        for h in ('ID','Date','Client','Total'):
            self.inv_tree.heading(h.lower(), text=h)
        self.inv_tree.pack(fill=tk.X)
        self.inv_tree.bind('<Double-1>', self.preview_invoice)

    def refresh_clients(self):
        clients = Db.get_clients()
        vals = [f"{c[0]} - {c[1]} {c[2]}" for c in clients]
        self.client_combo["values"] = vals
        if vals: self.client_combo.current(0)

    def add_client_popup(self):
        win = tk.Toplevel(self.root)
        win.title("Add Client")
        win.configure(bg='orange')
        entries = []
        labels = ["First Name", "Last Name", "Email", "Phone", "Address", "Postal Code", "Tax"]

        for i, l in enumerate(labels):
            tk.Label(win, text=l, bg='orange').grid(row=i, column=0, padx=6, pady=4, sticky='e')
            e = tk.Entry(win, bg='white')
            e.grid(row=i, column=1, padx=6, pady=4)
            entries.append(e)

        def save():
            tax_val = entries[-1].get().strip()
            if tax_val and Db.tax_exists(tax_val):
                messagebox.showerror("Error", f"Client with Tax {tax_val} already exists")
                return
            Db.add_client(*[e.get() for e in entries])
            self.refresh_clients()
            win.destroy()

        tk.Button(win, text="Save", bg='lightgreen', fg='black', command=save).grid(
            row=len(labels), column=0, columnspan=2, pady=10
        )

    def add_item(self):
        try:
            qty = float(self.qty.get())
            price = float(self.price.get())
        except:
            messagebox.showerror("Error", "Qty and Price must be numbers")
            return
        desc = self.desc.get()
        total = qty * price
        self.tree.insert("", "end", values=(desc, f"{qty:.2f}", f"{price:.2f}", f"{total:.2f}"))
        self.invoice_items.append({"desc": desc, "qty": qty, "price": price})
        self.update_totals()
        self.desc.delete(0, "end")
        self.qty.delete(0, "end")
        self.price.delete(0, "end")

    def remove_item(self):
        for sel in self.tree.selection():
            self.tree.delete(sel)
        self.invoice_items.clear()
        self.update_totals()

    def update_totals(self):
        subtotal = sum(i["qty"] * i["price"] for i in self.invoice_items)
        vat_amount = subtotal * self.vat_var.get() / 100
        total = subtotal + vat_amount
        self.subtotal_var.set(f"{subtotal:.2f}")
        self.total_var.set(f"{total:.2f}")

    def save_invoice(self):
        if not self.client_combo.get():
            messagebox.showerror("Error", "Select client")
            return
        client_id = int(self.client_combo.get().split(" - ")[0])
        date_str = self.date_entry.get_date().isoformat()
        subtotal = sum(i["qty"] * i["price"] for i in self.invoice_items)
        vat_amount = subtotal * self.vat_var.get() / 100
        total = subtotal + vat_amount
        inv_id = Db.add_invoice(client_id, date_str, subtotal, vat_amount, total)
        for it in self.invoice_items:
            Db.add_item(inv_id, it["desc"], it["qty"], it["price"], it["qty"]*it["price"])
        messagebox.showinfo("Saved", f"Invoice #{inv_id} saved")
        self.invoice_items.clear()
        self.tree.delete(*self.tree.get_children())
        self.update_totals()
        self.refresh_invoice_list()

    def refresh_invoice_list(self):
        self.inv_tree.delete(*self.inv_tree.get_children())
        
        self.inv_tree.column("id", anchor="center", width=50)
        self.inv_tree.column("date", anchor="center", width=100)
        self.inv_tree.column("client", anchor="center", width=200)
        self.inv_tree.column("total", anchor="center", width=80)
    
        for inv in Db.get_invoices():
            inv_id, date, client, total = inv
            self.inv_tree.insert("", "end", values=(
                inv_id,
                date,
                client,
                f"{total:.2f}"  
            ))

    def preview_invoice(self, _):
        sel = self.inv_tree.selection()
        if not sel:
            return
        inv_id = int(self.inv_tree.item(sel[0], "values")[0])
        items = Db.get_invoice_items(inv_id)

        win = tk.Toplevel(self.root)
        win.title(f"Invoice #{inv_id}")
        win.configure(bg='pink')

        frame = tk.Frame(win, bg='pink')
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(frame, columns=("desc", "qty", "price", "total"), show="headings", height=10, yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        tree.pack(fill=tk.BOTH, expand=True)
        
        tree.heading("desc", text="Description", anchor="center")
        tree.heading("qty", text="Qty", anchor="center")
        tree.heading("price", text="Price", anchor="center")
        tree.heading("total", text="Total", anchor="center")

        tree.column("desc", anchor="center", width=200)
        tree.column("qty", anchor="center", width=80)
        tree.column("price", anchor="center", width=80)
        tree.column("total", anchor="center", width=80)

        subtotal = 0
        for item in items:
            desc, qty, price, total_item = item
            tree.insert("", "end", values=(
                desc,
                f"{float(qty):.2f}",
                f"{float(price):.2f}",
                f"{float(total_item):.2f}"
            ))
            subtotal += total_item
            
        vat_rate = 24  # 24%
        vat_amount = subtotal * vat_rate / 100
        total = subtotal + vat_amount
        
        summary_frame = tk.Frame(win, bg='pink')
        summary_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(summary_frame, text=f"Subtotal: {subtotal:.2f}", width=25, anchor="center", bg='pink').pack()
        tk.Label(summary_frame, text=f"VAT ({vat_rate}%): {vat_amount:.2f}", width=25, anchor="center", bg='pink').pack()
        tk.Label(summary_frame, text=f"Total: {total:.2f}", width=25, anchor="center", font=("Arial", 10, "bold"), bg='pink').pack()


    def export_pdf(self):
        sel = self.inv_tree.selection()
        if not sel: return
        inv_id = int(self.inv_tree.item(sel[0], "values")[0])
        file = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not file: return
        export_invoice_pdf(Db, inv_id, file)
        messagebox.showinfo("PDF", f"Exported to {file}")
