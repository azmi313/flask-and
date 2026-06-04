from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

application = Flask(__name__)

# Deteksi environment (Railway atau lokal)
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL')

if IS_RAILWAY:
    # Mode Production (Railway) - Pakai PostgreSQL
    import psycopg2
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    def get_db_connection():
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    
    def init_db():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS buku (
                id VARCHAR(4) PRIMARY KEY,
                judul VARCHAR(40) NOT NULL,
                penulis VARCHAR(25) NOT NULL,
                penerbit VARCHAR(30) NOT NULL
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Database PostgreSQL initialized on Railway!")
    
    def execute_query(query, params=None, fetch_one=False, fetch_all=False):
        conn = get_db_connection()
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        result = None
        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        
        conn.commit()
        cur.close()
        conn.close()
        return result

else:
    # Mode Development (Lokal) - Pakai SQLite
    application.config['DB_NAME'] = os.path.join(os.getcwd(), 'database.db')
    
    def get_db_connection():
        conn = sqlite3.connect(application.config['DB_NAME'])
        return conn
    
    def init_db():
        if not os.path.exists(application.config['DB_NAME']):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE buku (
                    id TEXT PRIMARY KEY,
                    judul TEXT NOT NULL,
                    penulis TEXT NOT NULL,
                    penerbit TEXT NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
            print("Database SQLite created locally!")
    
    def execute_query(query, params=None, fetch_one=False, fetch_all=False):
        conn = get_db_connection()
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        result = None
        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        
        conn.commit()
        conn.close()
        return result

# Route: Halaman utama
@application.route('/')
def index():
    if IS_RAILWAY:
        # PostgreSQL version
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM buku ORDER BY id')
        container = cur.fetchall()
        cur.close()
        conn.close()
    else:
        # SQLite version
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM buku ORDER BY id')
        container = cur.fetchall()
        conn.close()
    
    return render_template('index.html', container=container)

# Route: Tambah data
@application.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        id = request.form['id']
        judul = request.form['judul']
        penulis = request.form['penulis']
        penerbit = request.form['penerbit']
        
        if IS_RAILWAY:
            # PostgreSQL version
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO buku VALUES (%s, %s, %s, %s)',
                       (id, judul, penulis, penerbit))
            conn.commit()
            cur.close()
            conn.close()
        else:
            # SQLite version
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO buku VALUES (?, ?, ?, ?)',
                       (id, judul, penulis, penerbit))
            conn.commit()
            conn.close()
        
        return redirect(url_for('index'))
    else:
        return render_template('tambah_form.html')

# Route: Ubah data
@application.route('/ubah/<id>', methods=['GET', 'POST'])
def ubah(id):
    if request.method == 'POST':
        judul = request.form['judul']
        penulis = request.form['penulis']
        penerbit = request.form['penerbit']
        
        if IS_RAILWAY:
            # PostgreSQL version
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE buku SET judul=%s, penulis=%s, penerbit=%s WHERE id=%s',
                       (judul, penulis, penerbit, id))
            conn.commit()
            cur.close()
            conn.close()
        else:
            # SQLite version
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE buku SET judul=?, penulis=?, penerbit=? WHERE id=?',
                       (judul, penulis, penerbit, id))
            conn.commit()
            conn.close()
        
        return redirect(url_for('index'))
    else:
        # Ambil data berdasarkan ID untuk ditampilkan di form
        if IS_RAILWAY:
            # PostgreSQL version
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM buku WHERE id=%s', (id,))
            buku = cur.fetchone()
            cur.close()
            conn.close()
        else:
            # SQLite version
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM buku WHERE id=?', (id,))
            buku = cur.fetchone()
            conn.close()
        
        return render_template('ubah_form.html', buku=buku)

# Route: Hapus data
@application.route('/hapus/<id>')
def hapus(id):
    if IS_RAILWAY:
        # PostgreSQL version
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM buku WHERE id=%s', (id,))
        conn.commit()
        cur.close()
        conn.close()
    else:
        # SQLite version
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM buku WHERE id=?', (id,))
        conn.commit()
        conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=True)