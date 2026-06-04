from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import sqlite3
from export_pdf import generate_buku_pdf, generate_hash
import tempfile

application = Flask(__name__)

# Database path untuk Railway
DB_PATH = '/tmp/database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS buku (
            id TEXT PRIMARY KEY,
            judul TEXT NOT NULL,
            penulis TEXT NOT NULL,
            penerbit TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("✓ Database SQLite initialized at:", DB_PATH)

# Initialize database
init_db()

@application.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM buku ORDER BY id')
    container = cur.fetchall()
    conn.close()
    return render_template('index.html', container=container)

@application.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        id_buku = request.form['id']
        judul = request.form['judul']
        penulis = request.form['penulis']
        penerbit = request.form['penerbit']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO buku VALUES (?, ?, ?, ?)', 
                   (id_buku, judul, penulis, penerbit))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('tambah_form.html')

@application.route('/ubah/<id>', methods=['GET', 'POST'])
def ubah(id):
    if request.method == 'POST':
        judul = request.form['judul']
        penulis = request.form['penulis']
        penerbit = request.form['penerbit']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('UPDATE buku SET judul=?, penulis=?, penerbit=? WHERE id=?',
                   (judul, penulis, penerbit, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM buku WHERE id=?', (id,))
    buku = cur.fetchone()
    conn.close()
    return render_template('ubah_form.html', buku=buku)

@application.route('/hapus/<id>')
def hapus(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM buku WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ROUTE EXPORT PDF
@application.route('/export-pdf')
def export_pdf():
    # Ambil semua data dari database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM buku ORDER BY id')
    data_buku = cur.fetchall()
    conn.close()
    
    if not data_buku:
        return "Tidak ada data untuk diexport", 400
    
    # Generate PDF
    pdf_file = generate_buku_pdf(data_buku)
    
    # Kirim file PDF ke user
    return send_file(
        pdf_file,
        as_attachment=True,
        download_name="laporan_buku.pdf",
        mimetype='application/pdf'
    )

# Route untuk melihat hash (tanda tangan digital)
@application.route('/hash')
def view_hash():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM buku ORDER BY id')
    data_buku = cur.fetchall()
    conn.close()
    
    hash_value = generate_hash(data_buku)
    return f"""
    <html>
    <head><title>Digital Signature</title></head>
    <body>
        <h2>Tanda Tangan Digital</h2>
        <p><b>Message Digest (SHA-256):</b></p>
        <p><code style="font-size:16px; color:blue;">{hash_value}</code></p>
        <p><a href="/">Kembali</a></p>
    </body>
    </html>
    """

@application.route('/health')
def health():
    return {"status": "ok", "message": "Flask app is running"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    application.run(host='0.0.0.0', port=port, debug=False)