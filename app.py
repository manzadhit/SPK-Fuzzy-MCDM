# app.py
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import sqlite3
import os
from fuzzy_logic import criteria_type, fuzzify_criteria, criteria_weights, calculate_final_ranking, calculate_topsis_with_steps

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

    rankings = calculate_final_ranking(data)

    # Menambahkan statistik
    stats = {
        'total_umkm': len(rankings),
        'sangat_potensial': len([r for r in rankings if r['kategori'] == "Sangat Potensial"]),
        'potensial': len([r for r in rankings if r['kategori'] == "Potensial"]),
        'cukup_potensial': len([r for r in rankings if r['kategori'] == "Cukup Potensial"]),
        'kurang_potensial': len([r for r in rankings if r['kategori'] == "Kurang Potensial"]),
        'tidak_potensial': len([r for r in rankings if r['kategori'] == "Tidak Potensial"])
    }

    return render_template('result.html', rankings=rankings, stats=stats)


@app.route('/detail/<nama>')
def detail(nama):
    conn = get_db_connection()
    umkm_list = conn.execute('SELECT * FROM umkm').fetchall()
    umkm = conn.execute(
        'SELECT * FROM umkm WHERE nama = ?', (nama,)).fetchone()
    conn.close()

    if not umkm:
        return redirect(url_for('index'))

    # Convert semua data untuk perhitungan
    all_data = [dict(row) for row in umkm_list]
    for d in all_data:
        d.pop('id', None)

    # Hitung TOPSIS dengan langkah-langkah
    scores, steps = calculate_topsis_with_steps(all_data)

    # Temukan index UMKM yang sedang dilihat
    umkm_index = next(i for i, d in enumerate(all_data) if d['nama'] == nama)

    data = dict(umkm)
    data.pop('id', None)

    # Hitung nilai fuzzy untuk setiap kriteria
    fuzzy_values = {}
    for criteria in criteria_type.keys():
        if criteria != 'nama':
            fuzzy_values[criteria] = fuzzify_criteria(data[criteria], criteria)

    detail_data = {
        'umkm': data,
        'fuzzy_values': fuzzy_values,
        'criteria_type': criteria_type,
        'criteria_weights': criteria_weights,
        'calculation_steps': {
            'matrix_row': steps['matrix'][umkm_index],
            'normalized_row': steps['normalized_matrix'][umkm_index],
            'weighted_row': steps['weighted_matrix'][umkm_index],
            'ideal_positive': steps['ideal_positive'],
            'ideal_negative': steps['ideal_negative'],
            'positive_distance': steps['positive_distance'][umkm_index],
            'negative_distance': steps['negative_distance'][umkm_index],
            'final_score': steps['final_scores'][umkm_index]
        }
    }

    return render_template('detail.html', data=detail_data)

@app.route('/reset')
def reset():
    conn = get_db_connection()
    conn.execute('DELETE FROM umkm')
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("port", 8080)))
