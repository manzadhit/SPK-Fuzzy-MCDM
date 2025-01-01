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
    'omzet': 0.2,
    'aset': 0.2,
    'jumlah_karyawan': 0.15,
    'modal_sendiri': 0.15,
    'kapasitas_produksi': 0.15,
    'pinjaman_bank': 0.15
}

criteria_type = {
    'omzet': 'cost',
    'aset': 'cost',
    'jumlah_karyawan': 'cost',
    'modal_sendiri': 'cost',
    'kapasitas_produksi': 'cost',
    'pinjaman_bank': 'benefit'
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
