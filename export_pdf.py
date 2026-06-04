from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
import hashlib
import datetime
import os
import qrcode
from PIL import Image as PILImage

def generate_buku_pdf(data_buku):
    """Generate PDF laporan data buku dengan QR Code"""
    
    temp_dir = "temp_pdf"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Generate hash
    data_string = ""
    for buku in data_buku:
        data_string += f"{buku[0]}{buku[1]}{buku[2]}{buku[3]}"
    sha256_hash = hashlib.sha256(data_string.encode()).hexdigest()
    
    # Buat QR Code
    qr_data = f"https://flask-and-production.up.railway.app/verify?hash={sha256_hash}"
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
    
    # Style custom
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        spaceAfter=20,
        textColor=colors.HexColor('#1a56db')
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.grey
    )
    
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=9,
        alignment=0,
        spaceAfter=5
    )
    
    # Konten PDF
    story = []
    
    # Header
    story.append(Paragraph("<b>LAPORAN DATA BUKU</b>", title_style))
    story.append(Paragraph(f"Dicetak: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", header_style))
    story.append(Spacer(1, 15))
    
    # Tabel data
    table_data = []
    table_data.append(['ID', 'Judul Buku', 'Penulis', 'Penerbit'])
    
    for buku in data_buku:
        table_data.append([
            str(buku[0]),
            str(buku[1]),
            str(buku[2]),
            str(buku[3])
        ])
    
    table = Table(table_data, colWidths=[2.5*cm, 5.5*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a56db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 25))
    
    # Tanda Tangan Digital dengan QR Code
    story.append(Paragraph("<b>TANDA TANGAN DIGITAL</b>", signature_style))
    story.append(Spacer(1, 5))
    
    # Tabel untuk QR Code dan Hash
    qr_table_data = [
        ['', ''],
        [Image(qr_path, width=2.5*cm, height=2.5*cm), 
         Paragraph(f"<b>SHA-256 Hash:</b><br/><font color='#1a56db' size='8'>{sha256_hash}</font><br/><br/><b>Verifikasi:</b><br/>Scan QR Code atau klik link verifikasi")]
    ]
    
    qr_table = Table(qr_table_data, colWidths=[4*cm, 10*cm])
    qr_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(qr_table)
    story.append(Spacer(1, 20))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,
        textColor=colors.grey
    )
    story.append(Paragraph("Dokumen ini ditandatangani secara digital", footer_style))
    
    doc.build(story)
    
    # Hapus QR Code temp
    os.remove(qr_path)
    
    return filename