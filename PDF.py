
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def export_invoice_pdf(db, invoice_id, filename):
    inv = db.get_invoices()
    inv_data = None
    for i in inv:
        if i[0] == invoice_id:
            inv_data = i
            break
    if not inv_data:
        raise ValueError("Invoice not found")

    clients = db.get_clients()
    client_data = next((c for c in clients if c[0] == inv_data[0]), None)

    items = db.get_invoice_items(invoice_id)

    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    story.append(Paragraph(f"Invoice #{invoice_id}", styles['Title']))
    story.append(Paragraph(f"Date: {inv_data[1]}", styles['Normal']))
    story.append(Paragraph(f"Client: {inv_data[2]}", styles['Normal']))
    if client_data and client_data[7]:
        story.append(Paragraph(f"Tax ID: {client_data[7]}", styles['Normal']))
    story.append(Spacer(1, 12))

    data = [['Description', 'Qty', 'Price', 'Total']]
    for row in items:
        desc, qty, price, total = row
        data.append([desc, str(qty), f"{price:.2f}", f"{total:.2f}"])

    table = Table(data, colWidths=[200, 50, 60, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(1,1),(-1,-1),'RIGHT'),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')
    ]))
    story.append(table)
    story.append(Spacer(1,12))

    # Σύνοψη
    subtotal = sum([row[3] for row in items])
    vat = subtotal * 0.24
    total = subtotal + vat
    summary_data = [
        ['Subtotal', f"{subtotal:.2f}"],
        ['VAT (24%)', f"{vat:.2f}"],
        ['Total', f"{total:.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[300, 80])
    summary_table.setStyle(TableStyle([
        ('ALIGN',(1,0),(-1,-1),'RIGHT'),
        ('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold')
    ]))
    story.append(summary_table)

    doc.build(story)
