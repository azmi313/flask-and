from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from export_pdf import generate_buku_pdf
import hashlib

application = Flask(__name__)

# Deteksi environment
IS_WINDOWS = os.name == 'nt'
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL')

# Database connection
def get_db_connection():
    if IS_RAILWAY:
        # PostgreSQL untuk Railway
        DATABASE_URL = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        # SQLite untuk lokal
        DB_PATH = os.path.join(os.getcwd(), 'database.db')
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if IS_RAILWAY:
        # PostgreSQL query
        cur.execute('''
            CREATE TABLE IF NOT EXISTS buku (
                id VARCHAR(4) PRIMARY KEY,
                judul VARCHAR(40) NOT NULL,
                penulis VARCHAR(25) NOT NULL,
                penerbit VARCHAR(30) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ PostgreSQL database initialized on Railway!")
    else:
        # SQLite query
        cur.execute('''
            CREATE TABLE IF NOT EXISTS buku (
                id TEXT PRIMARY KEY,
                judul TEXT NOT NULL,
                penulis TEXT NOT NULL,
                penerbit TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print(f"✓ SQLite database initialized at: {os.path.join(os.getcwd(), 'database.db')}")
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

@application.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM buku ORDER BY id')
    
    if IS_RAILWAY:
        rows = cur.fetchall()
        # Convert PostgreSQL rows to list of tuples for compatibility
        container = [(row[0], row[1], row[2], row[3]) for row in rows]
    else:
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
        
        if IS_RAILWAY:
            cur.execute('INSERT INTO buku (id, judul, penulis, penerbit) VALUES (%s, %s, %s, %s)',
                       (id_buku, judul, penulis, penerbit))
        else:
            cur.execute('INSERT INTO buku (id, judul, penulis, penerbit) VALUES (?, ?, ?, ?)',
                       (id_buku, judul, penulis, penerbit))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('tambah_form.html')

@application.route('/ubah/<id>', methods=['GET', 'POST'])
def ubah(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        judul = request.form['judul']
        penulis = request.form['penulis']
        penerbit = request.form['penerbit']
        
        if IS_RAILWAY:
            cur.execute('UPDATE buku SET judul=%s, penulis=%s, penerbit=%s WHERE id=%s',
                       (judul, penulis, penerbit, id))
        else:
            cur.execute('UPDATE buku SET judul=?, penulis=?, penerbit=? WHERE id=?',
                       (judul, penulis, penerbit, id))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    # GET request - ambil data untuk ditampilkan
    if IS_RAILWAY:
        cur.execute('SELECT * FROM buku WHERE id=%s', (id,))
    else:
        cur.execute('SELECT * FROM buku WHERE id=?', (id,))
    
    buku = cur.fetchone()
    conn.close()
    return render_template('ubah_form.html', buku=buku)

@application.route('/hapus/<id>')
def hapus(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if IS_RAILWAY:
        cur.execute('DELETE FROM buku WHERE id=%s', (id,))
    else:
        cur.execute('DELETE FROM buku WHERE id=?', (id,))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@application.route('/export-pdf')
def export_pdf():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM buku ORDER BY id')
    
    if IS_RAILWAY:
        rows = cur.fetchall()
        data_buku = [(row[0], row[1], row[2], row[3]) for row in rows]
    else:
        data_buku = cur.fetchall()
    
    conn.close()
    
    if not data_buku:
        return "<h3>Tidak ada data untuk diexport. Silakan tambah data terlebih dahulu.</h3><a href='/'>Kembali</a>", 400
    
    pdf_file = generate_buku_pdf(data_buku)
    
    return send_file(
        pdf_file,
        mimetype='application/pdf'
    )

@application.route('/health')
def health():
    return {"status": "ok", "message": "Flask app is running", "database": "PostgreSQL" if IS_RAILWAY else "SQLite"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=True)