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
    """Generate PDF laporan data buku dengan QR Code"""
    
    temp_dir = "temp_pdf"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Generate hash dari data
    data_string = ""
    for buku in data_buku:
        data_string += f"{buku[0]}{buku[1]}{buku[2]}{buku[3]}"
    sha256_hash = hashlib.sha256(data_string.encode()).hexdigest()
    
    # Buat QR Code
    qr_data = f"Hash: {sha256_hash}\nTanggal: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_path = os.path.join(temp_dir, f"qrcode_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    qr_img.save(qr_path)
    
    # Nama file PDF
    filename = os.path.join(temp_dir, f"laporan_buku_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        spaceAfter=20,
        textColor=colors.HexColor('#1a56db')
    )
    
    story = []
    story.append(Paragraph("<b>LAPORAN DATA BUKU</b>", title_style))
    story.append(Paragraph(f"Dicetak: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                          ParagraphStyle('Header', parent=styles['Normal'], fontSize=10, alignment=1)))
    story.append(Spacer(1, 15))
    
    # Tabel data
    table_data = [['ID', 'Judul Buku', 'Penulis', 'Penerbit']]
    for buku in data_buku:
        table_data.append([str(buku[0]), str(buku[1]), str(buku[2]), str(buku[3])])
    
    table = Table(table_data, colWidths=[2.5*cm, 5.5*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a56db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 25))
    
    # QR Code dan Hash
    story.append(Paragraph("<b>TANDA TANGAN DIGITAL</b>", 
                          ParagraphStyle('Signature', parent=styles['Normal'], fontSize=10)))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph(f"<b>SHA-256 Hash:</b><br/><font color='#1a56db'>{sha256_hash}</font>",
                          ParagraphStyle('Hash', parent=styles['Normal'], fontSize=9)))
    story.append(Spacer(1, 10))
    
    if os.path.exists(qr_path):
        story.append(Image(qr_path, width=3*cm, height=3*cm))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("Dokumen ini ditandatangani secara digital", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1)))
    
    doc.build(story)
    
    # Hapus QR Code temp
    if os.path.exists(qr_path):
        os.remove(qr_path)
    
    return filenamess