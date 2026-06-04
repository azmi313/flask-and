from flask import Flask, render_template, \
  request, redirect, url_for
import pysqlite3 as sqlite3
import os

application = Flask(__name__)

# Perbaiki path database
application.config['DB_NAME'] = os.path.join(os.getcwd(), 'database.db')

conn = cursor = None

def openDb():
    global conn, cursor
    conn = sqlite3.connect(application.config['DB_NAME'])
    cursor = conn.cursor()   

def closeDb():
    global conn, cursor
    cursor.close()
    conn.close()

@application.route('/')
def index():   
    openDb()
    container = []
    cursor.execute('SELECT * FROM buku')
    for row in cursor.fetchall():
        container.append(row)
    closeDb()
    return render_template('index.html', container=container)

@application.route('/tambah', methods=['GET','POST'])
def tambah():
    if request.method == 'POST':
        id = request.form['id']
        judul = request.form['judul']
        penulis = request.form['penulis']
        penerbit = request.form['penerbit']
        data = (id, judul, penulis, penerbit)
        openDb()
        cursor.execute('INSERT INTO buku VALUES(?,?,?,?)', data)
        conn.commit()
        closeDb()
        return redirect(url_for('index'))
    else:
        return render_template('tambah_form.html')

@application.route('/ubah/<id>', methods=['GET','POST'])
def ubah(id):
    openDb()
    cursor.execute('SELECT * FROM buku WHERE id=?', (id,))
    buku = cursor.fetchone()
    closeDb()
    
    if request.method == 'POST':
        judul = request.form['judul']
        penulis = request.form['penulis']
        penerbit = request.form['penerbit']
        openDb()
        cursor.execute('''
            UPDATE buku SET judul=?, penulis=?, penerbit=? 
            WHERE id=?
        ''', (judul, penulis, penerbit, id))
        conn.commit()
        closeDb()
        return redirect(url_for('index'))
    else:
        return render_template('ubah_form.html', buku=buku)

@application.route('/hapus/<id>', methods=['GET','POST'])
def hapus(id):
    openDb()
    cursor.execute('DELETE FROM buku WHERE id=?', (id,))
    conn.commit()
    closeDb()
    return redirect(url_for('index'))

# Buat database jika belum ada
def init_db():
    if not os.path.exists(application.config['DB_NAME']):
        conn = sqlite3.connect(application.config['DB_NAME'])
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE buku (
                id TEXT PRIMARY KEY,
                judul TEXT NOT NULL,
                penulis TEXT NOT NULL,
                penerbit TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("Database created successfully with pysqlite3!")

if __name__ == '__main__':
    init_db()  # Inisialisasi database
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)