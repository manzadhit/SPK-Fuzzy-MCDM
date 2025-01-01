import sqlite3

DATABASE = 'umkm.db'

conn = sqlite3.connect(DATABASE)
conn.execute('''
CREATE TABLE umkm (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    omzet REAL NOT NULL,
    aset REAL NOT NULL,
    jumlah_karyawan INTEGER NOT NULL,
    modal_sendiri REAL NOT NULL,
    kapasitas_produksi INTEGER NOT NULL,
    pinjaman_bank REAL NOT NULL
);
''')
conn.close()
