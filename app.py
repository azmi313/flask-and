from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

application = Flask(__name__)

# Detect environment
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL')
DATABASE_URL = os.environ.get('DATABASE_URL') if IS_RAILWAY else None

def get_db_connection():
    """Get database connection with error handling"""
    
    if IS_RAILWAY:
        # Mode Production (Railway) - Pakai PostgreSQL
        import psycopg2_binary as psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        # Mode Development (Lokal) - Pakai SQLite
        db_path = os.path.join(os.getcwd(), 'database.db')
        conn = sqlite3.connect(db_path)
        return conn

def init_db():
    """Initialize database"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if IS_RAILWAY:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS buku (
                    id VARCHAR(4) PRIMARY KEY,
                    judul VARCHAR(40) NOT NULL,
                    penulis VARCHAR(25) NOT NULL,
                    penerbit VARCHAR(30) NOT NULL
                )
            ''')
        else:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS buku (
                    id TEXT PRIMARY KEY,
                    judul TEXT NOT NULL,
                    penulis TEXT NOT NULL,
                    penerbit TEXT NOT NULL
                )
            ''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"⚠ Database initialization warning: {e}")

# Initialize DB on app startup
try:
    init_db()
except:
    print("⚠ Continuing without database initialization")

@application.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM buku ORDER BY id')
        container = cur.fetchall()
        conn.close()
        return render_template('index.html', container=container)
    except Exception as e:
        return f"<h1>Database Error</h1><p>{str(e)}</p>", 500

@application.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        try:
            id_buku = request.form['id']
            judul = request.form['judul']
            penulis = request.form['penulis']
            penerbit = request.form['penerbit']
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            if IS_RAILWAY:
                cur.execute('INSERT INTO buku VALUES (%s, %s, %s, %s)',
                           (id_buku, judul, penulis, penerbit))
            else:
                cur.execute('INSERT INTO buku VALUES (?, ?, ?, ?)',
                           (id_buku, judul, penulis, penerbit))
            
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p>", 500
    else:
        return render_template('tambah_form.html')

@application.route('/ubah/<id>', methods=['GET', 'POST'])
def ubah(id):
    if request.method == 'POST':
        try:
            judul = request.form['judul']
            penulis = request.form['penulis']
            penerbit = request.form['penerbit']
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            if IS_RAILWAY:
                cur.execute('UPDATE buku SET judul=%s, penulis=%s, penerbit=%s WHERE id=%s',
                           (judul, penulis, penerbit, id))
            else:
                cur.execute('UPDATE buku SET judul=?, penulis=?, penerbit=? WHERE id=?',
                           (judul, penulis, penerbit, id))
            
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p>", 500
    else:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            if IS_RAILWAY:
                cur.execute('SELECT * FROM buku WHERE id=%s', (id,))
            else:
                cur.execute('SELECT * FROM buku WHERE id=?', (id,))
            
            buku = cur.fetchone()
            conn.close()
            return render_template('ubah_form.html', buku=buku)
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p>", 500

@application.route('/hapus/<id>')
def hapus(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if IS_RAILWAY:
            cur.execute('DELETE FROM buku WHERE id=%s', (id,))
        else:
            cur.execute('DELETE FROM buku WHERE id=?', (id,))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", 500

@application.route('/health')
def health():
    return {"status": "ok", "message": "Flask app is running"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    application.run(host='0.0.0.0', port=port, debug=False)