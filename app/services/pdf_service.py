import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_quotation_pdf(order_id: int, customer_name: str, phone: str, event_type: str, items: list, total: float) -> str:
    os.makedirs("app/static/pdf", exist_ok=True)
    pdf_filename = f"app/static/pdf/Quotation_Order_{order_id}.pdf"
    
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#3b2011'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#d97706'),
        spaceAfter=15
    )
    
    story.append(Paragraph("The MunchBox by Aunty Bree's", title_style))
    story.append(Paragraph("Official Order Quotation & Banking Details", subtitle_style))
    
    info_data = [
        [Paragraph(f"<b>Order ID:</b> #{order_id}", styles['Normal']), Paragraph(f"<b>Event Type:</b> {event_type}", styles['Normal'])],
        [Paragraph(f"<b>Customer:</b> {customer_name}", styles['Normal']), Paragraph(f"<b>Phone:</b> {phone}", styles['Normal'])],
        [Paragraph(f"<b>Pickup Address:</b> 19 Eastwood Road, Rosebank, Gauteng, 2091", styles['Normal']), Paragraph(f"<b>Contact:</b> 068 016 2552", styles['Normal'])]
    ]
    
    info_table = Table(info_data, colWidths=[270, 270])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fdf8f0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#f59e0b')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    table_data = [["Item Description", "Qty", "Unit Price", "Total"]]
    for item in items:
        table_data.append([item.name, str(item.qty), f"R {item.price:.2f}", f"R {item.price * item.qty:.2f}"])
    
    table_data.append(["", "", "Total Amount:", f"R {total:.2f}"])
    
    item_table = Table(table_data, colWidths=[260, 60, 110, 110])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3b2011')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-2), colors.white),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#d1d5db')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#fdf8f0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 20))
    
    bank_text = (
        "<b>Banking Details for Deposit:</b><br/>"
        "<b>Account Holder:</b> Doone B Johns<br/>"
        "<b>Bank:</b> Capitec Bank<br/>"
        "<b>Account Number:</b> 160 351 9228<br/>"
        "<i>Please upload your proof of payment on the website or send via WhatsApp to secure your order.</i>"
    )
    
    bank_table = Table([[Paragraph(bank_text, styles['Normal'])]], colWidths=[540])
    bank_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fdf8f0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3b2011')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(bank_table)
    
    doc.build(story)
    return pdf_filename