
import sqlite3

DB_FILE = "invoice.db"

def create_database():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            postal_code TEXT,
            tax TEXT UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            date TEXT,
            subtotal REAL,
            vat REAL,
            total REAL,
            notes TEXT,
            FOREIGN KEY(client_id) REFERENCES clients(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            description TEXT,
            qty REAL,
            price REAL,
            total REAL,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id)
        )
    """)

    conn.commit()
    conn.close()

def add_client(first_name, last_name="", email="", phone="", address="", postal_code="", tax=""):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clients (first_name, last_name, email, phone, address, postal_code, tax)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, email, phone, address, postal_code, tax))
    conn.commit()
    client_id = cur.lastrowid
    conn.close()
    return client_id

def get_clients():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, last_name, email, phone, address, postal_code, tax FROM clients")
    rows = cur.fetchall()
    conn.close()
    return rows

def tax_exists(tax):
    """Ελέγχει αν υπάρχει ήδη πελάτης με αυτό το Tax"""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id FROM clients WHERE tax=?", (tax,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def add_invoice(client_id, date_str, subtotal, vat, total, notes=""):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO invoices (client_id, date, subtotal, vat, total, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (client_id, date_str, subtotal, vat, total, notes))
    conn.commit()
    inv_id = cur.lastrowid
    conn.close()
    return inv_id

def get_invoices():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT invoices.id, invoices.date, clients.first_name || ' ' || clients.last_name, invoices.total
        FROM invoices
        LEFT JOIN clients ON invoices.client_id = clients.id
        ORDER BY invoices.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def add_item(invoice_id, description, qty, price, total):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO items (invoice_id, description, qty, price, total)
        VALUES (?, ?, ?, ?, ?)
    """, (invoice_id, description, qty, price, total))
    conn.commit()
    item_id = cur.lastrowid
    conn.close()
    return item_id

def get_invoice_items(invoice_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT description, qty, price, total FROM items WHERE invoice_id=?", (invoice_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
