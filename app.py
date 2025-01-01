# app.py
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import sqlite3
import os
from fuzzy_logic import calculate_topsis

app = Flask(__name__)
DATABASE = 'umkm.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    umkm_list = conn.execute('SELECT * FROM umkm').fetchall()
    conn.close()
    return render_template('index.html', data=umkm_list)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO umkm (nama, omzet, aset, jumlah_karyawan, modal_sendiri, kapasitas_produksi, pinjaman_bank) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (request.form['nama'], float(request.form['omzet']), float(request.form['aset']),
             int(request.form['jumlah_karyawan']), float(
                 request.form['modal_sendiri']),
             int(request.form['kapasitas_produksi']), float(request.form['pinjaman_bank']))
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.csv'):
        return redirect(request.url)

    df = pd.read_csv(file)
    conn = get_db_connection()
    for _, row in df.iterrows():
        conn.execute(
            'INSERT INTO umkm (nama, omzet, aset, jumlah_karyawan, modal_sendiri, kapasitas_produksi, pinjaman_bank) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (row['nama'], float(row['omzet']), float(row['aset']),
             int(row['jumlah_karyawan']), float(row['modal_sendiri']),
             int(row['kapasitas_produksi']), float(row['pinjaman_bank']))
        )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/result')
def result():
    conn = get_db_connection()
    umkm_list = conn.execute('SELECT * FROM umkm').fetchall()
    conn.close()

    if not umkm_list:
        return render_template('result.html', rankings=[])

    data = [dict(row) for row in umkm_list]
    for umkm in data:
        umkm.pop('id', None)

    scores = calculate_topsis(data)
    rankings = [{'nama': umkm['nama'], 'score': score}
                for umkm, score in zip(data, scores)]
    rankings.sort(key=lambda x: x['score'], reverse=True)

    return render_template('result.html', rankings=rankings)


@app.route('/reset')
def reset():
    conn = get_db_connection()
    conn.execute('DELETE FROM umkm')
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("port", 8080)))
