from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import os
import sqlite3
from export_pdf import generate_buku_pdf
import hashlib
import json

application = Flask(__name__)

# Static folder configuration
application.config['STATIC_FOLDER'] = 'static'

# Deteksi environment
IS_WINDOWS = os.name == 'nt'

if IS_WINDOWS:
    DB_PATH = os.path.join(os.getcwd(), 'database.db')
else:
    DB_PATH = '/tmp/database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if IS_WINDOWS:
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS buku (
            id TEXT PRIMARY KEY,
            judul TEXT NOT NULL,
            penulis TEXT NOT NULL,
            penerbit TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✓ Database initialized at: {DB_PATH}")

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
        cur.execute('INSERT INTO buku VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)', 
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

@application.route('/export-pdf')
def export_pdf():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM buku ORDER BY id')
    data_buku = cur.fetchall()
    conn.close()
    
    if not data_buku:
        return "<h3>Tidak ada data untuk diexport. Silakan tambah data terlebih dahulu.</h3><a href='/'>Kembali</a>", 400
    
    pdf_file = generate_buku_pdf(data_buku)
    
    return send_file(
        pdf_file,
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=True)