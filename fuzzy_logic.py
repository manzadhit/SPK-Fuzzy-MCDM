# fuzzy_logic.py
import numpy as np


def fuzzy_membership(x, a, b, c):
   if x <= a or x >= c:
       return 0
   elif a < x <= b:
       return (x - a) / (b - a)
   else:
       return (c - x) / (c - b)


def fuzzify_criteria(value, criteria):
   fuzzy_sets = {
       'omzet': {
           'rendah': (0, 50, 100),
           'sedang': (75, 150, 225),
           'tinggi': (200, 300, 400)
       },
       'aset': {
           'rendah': (0, 100, 200),
           'sedang': (150, 300, 450),
           'tinggi': (400, 600, 800)
       },
       'jumlah_karyawan': {
           'sedikit': (0, 5, 10),
           'sedang': (8, 15, 22),
           'banyak': (20, 30, 40)
       },
       'modal_sendiri': {
           'rendah': (0, 25, 50),
           'sedang': (40, 75, 110),
           'tinggi': (100, 150, 200)
       },
       'kapasitas_produksi': {
           'rendah': (0, 100, 200),
           'sedang': (150, 300, 450),
           'tinggi': (400, 600, 800)
       },
       'pinjaman_bank': {
           'rendah': (0, 25, 50),
           'sedang': (40, 75, 110),
           'tinggi': (100, 150, 200)
       }
   }
   
   memberships = {}
   for label, (a, b, c) in fuzzy_sets[criteria].items():
       memberships[label] = fuzzy_membership(value, a, b, c)
   return memberships


criteria_weights = {
    'omzet': 0.25,
    'aset': 0.20,
    'jumlah_karyawan': 0.15,
    'modal_sendiri': 0.15,
    'kapasitas_produksi': 0.15,
    'pinjaman_bank': 0.10
}

criteria_type = {
    'omzet': 'cost',      # Semakin kecil omzet, semakin membutuhkan bantuan
    'aset': 'cost',       # Semakin kecil aset, semakin membutuhkan bantuan
    'jumlah_karyawan': 'benefit',  # Semakin banyak karyawan, semakin perlu dipertahankan
    'modal_sendiri': 'cost',    # Semakin kecil modal sendiri, semakin butuh bantuan
    # Semakin tinggi kapasitas, menunjukkan potensi berkembang
    'kapasitas_produksi': 'benefit',
    'pinjaman_bank': 'cost'  # Semakin tinggi pinjaman, semakin berisiko
}


def calculate_topsis(data):
   # Fuzzifikasi data
   fuzzy_data = []
   for umkm in data:
       fuzzy_umkm = {}
       for criteria, value in umkm.items():
           if criteria != 'nama':
               fuzzy_umkm[criteria] = fuzzify_criteria(value, criteria)
       fuzzy_data.append(fuzzy_umkm)

   # Konversi ke matriks keputusan
   matrix = []
   for f_umkm in fuzzy_data:
       row = []
       for criteria in criteria_type.keys():
           row.append(max(f_umkm[criteria].values()))
       matrix.append(row)
   matrix = np.array(matrix)

   # Normalisasi matriks fuzzy
   norm_matrix = matrix / np.sqrt(np.sum(matrix**2, axis=0))

   # Pembobotan
   weighted_matrix = np.zeros_like(norm_matrix)
   for i, criteria in enumerate(criteria_type.keys()):
       weighted_matrix[:, i] = norm_matrix[:, i] * criteria_weights[criteria]

   # Solusi ideal positif & negatif
   ideal_pos = np.array([np.max(weighted_matrix[:, i]) if criteria_type[c] == 'benefit'
                        else np.min(weighted_matrix[:, i])
                        for i, c in enumerate(criteria_type.keys())])

   ideal_neg = np.array([np.min(weighted_matrix[:, i]) if criteria_type[c] == 'benefit'
                        else np.max(weighted_matrix[:, i])
                        for i, c in enumerate(criteria_type.keys())])

   # Hitung jarak
   pos_dist = np.sqrt(np.sum((weighted_matrix - ideal_pos)**2, axis=1))
   neg_dist = np.sqrt(np.sum((weighted_matrix - ideal_neg)**2, axis=1))

   # Hitung skor akhir
   scores = neg_dist / (pos_dist + neg_dist)
   return scores


def defuzzify_result(score):
    if score >= 0.8:
        return "Sangat Potensial"
    elif score >= 0.6:
        return "Potensial"
    elif score >= 0.4:
        return "Cukup Potensial"
    elif score >= 0.2:
        return "Kurang Potensial"
    else:
        return "Tidak Potensial"


def calculate_final_ranking(data):
    scores = calculate_topsis(data)
    rankings = []

    # Urutkan data berdasarkan score sebelum membuat ranking
    sorted_data = list(zip(data, scores))
    sorted_data.sort(key=lambda x: x[1], reverse=True)

    for i, (umkm, score) in enumerate(sorted_data):
        rankings.append({
            'rank': i + 1,  # Ranking akan berurutan karena data sudah diurutkan
            'nama': umkm['nama'],
            'score': round(score, 4),
            'kategori': defuzzify_result(score),
            'detail_scores': {
                criteria: umkm[criteria]
                for criteria in criteria_type.keys()
            }
        })

    return rankings  # Tidak perlu sort lagi karena sudah terurut
