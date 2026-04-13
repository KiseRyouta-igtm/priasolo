from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# buat tabel
def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS penerima (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            nik TEXT,
            alamat TEXT,
            jenis_bantuan TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 🔐 LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "123":
            session['login'] = True
            return redirect('/')
        else:
            return "Login gagal!"

    return render_template("login.html")

# 🔓 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# 🏠 HALAMAN UTAMA (DIPROTEKSI)
@app.route('/')
def index():
    if 'login' not in session:
        return redirect('/login')

    conn = get_db()
    data = conn.execute("SELECT * FROM penerima").fetchall()
    return render_template("index.html", data=data)

# ➕ TAMBAH DATA (DIPROTEKSI)
@app.route('/tambah', methods=['GET','POST'])
def tambah():
    if 'login' not in session:
        return redirect('/login')

    if request.method == 'POST':
        nama = request.form['nama']
        nik = request.form['nik']
        alamat = request.form['alamat']
        jenis = request.form['jenis']
        
        conn = get_db()

        # validasi NIK tidak boleh sama
        cek = conn.execute("SELECT * FROM penerima WHERE nik=?", (nik,)).fetchone()
        if cek:
            return "NIK sudah terdaftar!"

        conn.execute("INSERT INTO penerima (nama, nik, alamat, jenis_bantuan, status) VALUES (?,?,?,?,?)",
                     (nama, nik, alamat, jenis, "Belum Disalurkan"))
        conn.commit()
        return redirect('/')
    
    return render_template("tambah.html")

# 🔄 UPDATE STATUS
@app.route('/update/<int:id>')
def update(id):
    if 'login' not in session:
        return redirect('/login')

    conn = get_db()
    conn.execute("UPDATE penerima SET status='Sudah Disalurkan' WHERE id=?", (id,))
    conn.commit()
    return redirect('/')

# ❌ HAPUS DATA
@app.route('/hapus/<int:id>')
def hapus(id):
    if 'login' not in session:
        return redirect('/login')

    conn = get_db()
    conn.execute("DELETE FROM penerima WHERE id=?", (id,))
    conn.commit()
    return redirect('/')

# route
@app.route('/laporan')
def laporan():
    if 'login' not in session:
        return redirect('/login')

    conn = get_db()

    # ambil semua data
    data = conn.execute("SELECT * FROM penerima").fetchall()

    # statistik
    total = conn.execute("SELECT COUNT(*) FROM penerima").fetchone()[0]
    sudah = conn.execute("SELECT COUNT(*) FROM penerima WHERE status='Sudah Disalurkan'").fetchone()[0]
    belum = conn.execute("SELECT COUNT(*) FROM penerima WHERE status='Belum Disalurkan'").fetchone()[0]

    return render_template("laporan.html", data=data, total=total, sudah=sudah, belum=belum)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)