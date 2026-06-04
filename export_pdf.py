from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import hashlib
import datetime
import os
import qrcode

def generate_buku_pdf(data_buku):
    """Generate PDF laporan data buku"""
    
    # Buat folder temp
    temp_dir = "temp_pdf"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Generate hash dari data
    data_string = ""
    for buku in data_buku:
        data_string += f"{buku[0]}{buku[1]}{buku[2]}{buku[3]}"
    sha256_hash = hashlib.sha256(data_string.encode()).hexdigest()
    
    # Buat QR Code
    qr = qrcode.QRCode(version=1, box_size=6, border=1)
    qr.add_data(sha256_hash)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_path = os.path.join(temp_dir, f"qrcode_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    qr_img.save(qr_path)
    
    # Nama file PDF
    filename = os.path.join(temp_dir, f"laporan_buku_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    # Buat PDF
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    story = []
    
    # Judul Data Buku
    story.append(Paragraph("<b>Data Buku</b>", 
                          ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, alignment=0)))
    story.append(Spacer(1, 10))
    
    # Tabel
    table_data = [['Nip', 'Nama', 'Konsorsium', 'Angkatan']]
    for buku in data_buku:
        table_data.append([str(buku[0]), str(buku[1]), str(buku[2]), str(buku[3])])
    
    table = Table(table_data, colWidths=[3*cm, 5*cm, 4*cm, 3.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 25))
    
    # Tanda Tangan Digital
    story.append(Paragraph("<b>Tanda Tangan Digital</b>", styles['Normal']))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Message Digest (SHA-256):", 
                          ParagraphStyle('Label', parent=styles['Normal'], fontSize=10, alignment=0, fontName='Helvetica-Bold')))
    story.append(Spacer(1, 5))
    story.append(Paragraph(sha256_hash, 
                          ParagraphStyle('Hash', parent=styles['Normal'], fontSize=9, alignment=0, fontName='Courier')))
    story.append(Spacer(1, 10))
    
    # QR Code di bawah hash (rata kiri)
    if os.path.exists(qr_path):
        qr_image = Image(qr_path, width=3*cm, height=3*cm)
        qr_image.hAlign = 'LEFT'
        story.append(qr_image)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Dicetak pada: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=0)))
    
    # Build PDF
    doc.build(story)
    
    # Hapus QR Code temp
    if os.path.exists(qr_path):
        os.remove(qr_path)
    
    return filename