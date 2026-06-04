from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import hashlib
import datetime

def generate_buku_pdf(data_buku):
    """Generate PDF laporan data buku dengan tanda tangan digital"""
    
    # Nama file PDF
    filename = f"laporan_buku_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Buat PDF
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Center
        spaceAfter=30
    )
    
    # Konten PDF
    story = []
    
    # Judul
    title = Paragraph("<b>LAPORAN DATA BUKU</b>", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Data tabel
    table_data = []
    # Header
    table_data.append(['Nip', 'Nama', 'Konsorsium', 'Angkatan'])
    # Data
    for buku in data_buku:
        table_data.append([
            str(buku[0]),  # ID/Nip
            str(buku[1]),  # Judul/Nama
            str(buku[2]),  # Penulis/Konsorsium
            str(buku[3])   # Penerbit/Angkatan
        ])
    
    # Buat tabel
    table = Table(table_data, colWidths=[3*cm, 5*cm, 4*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Tanda Tangan Digital
    # Buat string data untuk di-hash
    data_string = ""
    for buku in data_buku:
        data_string += f"{buku[0]}{buku[1]}{buku[2]}{buku[3]}"
    
    # Generate SHA-256 hash
    sha256_hash = hashlib.sha256(data_string.encode()).hexdigest()
    
    # Tambahkan tanda tangan digital
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=10,
        alignment=0,
        spaceAfter=5
    )
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Tanda Tangan Digital</b>", signature_style))
    story.append(Paragraph(f"Message Digest (SHA-256):", signature_style))
    story.append(Paragraph(f"<font color='blue'><b>{sha256_hash}</b></font>", signature_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Dicetak pada: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", signature_style))
    
    # Build PDF
    doc.build(story)
    
    return filename

def generate_hash(data_buku):
    """Generate SHA-256 hash dari data buku"""
    data_string = ""
    for buku in data_buku:
        data_string += f"{buku[0]}{buku[1]}{buku[2]}{buku[3]}"
    return hashlib.sha256(data_string.encode()).hexdigest()