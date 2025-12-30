from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

DOCUMENTS = [
  {"id": 1, "title": "Pengembangan Sistem Informasi Geografis Pemetaan Lokasi UMKM Menggunakan Metode Waterfall. Penelitian ini membahas tentang perancangan dan implementasi SIG untuk membantu pemasaran produk UMKM di Denpasar.", "snippet": "...."},
  {"id": 2, "title": "Analisis Perbandingan Algoritma Klasifikasi Teks untuk Deteksi Sentimen pada Ulasan Produk Kecantikan. Metode TF-IDF dan Naive Bayes digunakan dalam analisis ini.", "snippet": "...."},
  {"id": 3, "title": "Perancangan Aplikasi Mobile untuk Peningkatan Efisiensi Distribusi Logistik Menggunakan Firebase Realtime Database. Aplikasi ini berfokus pada optimasi rute.", "snippet": "...."},
  {"id": 4, "title": "Implementasi Metode *Clustering* K-Means untuk Segmentasi Pasar Produk UMKM. Fokus utama adalah pada pengelompokan pelanggan berdasarkan minat pembelian.", "snippet": "...."},
  {"id": 5, "title": "lorem ipsum dolor st amet", "snippet": "...."},
  {"id": 6, "title": "lorem ipsum dolor st amet", "snippet": "...."},
  {"id": 7, "title": "lorem ipsum dolor st amet", "snippet": "...."},
  {"id": 8, "title": "lorem ipsum dolor st amet", "snippet": "...."},
  {"id": 9, "title": "lorem ipsum dolor st amet", "snippet": "...."},
]
text_corpus = [doc['title'] + " " + doc['snippet'] for doc in DOCUMENTS]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(text_corpus)
features = vectorizer.get_feature_names_out()

@app.route('/api/search', methods=['GET'])
def search_documents():
  query = request.args.get('q')
  if not query:
    return jsonify({"message": "Mohon masukan Quary Pencarian.", "result": []})
  print(f"\n[INFO] Query diterima: {query}")

  query_vector = vectorizer.transform([query])
  cosine_scores = cosine_similarity(query_vector, X).flatten()

  results = []
  for i, score in enumerate(cosine_scores):
    if score > 0.0:
      doc = DOCUMENTS[i].copy()
      doc['score'] = score
      doc['relevansi'] = f"{score*100:.2f}%"
      results.append(doc)

  results.sort(key=lambda x: x['score'], reverse=True)

  for rank, doc in enumerate(results, 1):
    doc['ranking'] = rank
  
  if results:
    print("Hasil Perengkingan Teratas:")
    for doc in results [:3]:
      print(f"[{doc['ranking']}] {doc['title'][:50]}... | Skor: {doc['relevansi']}")
  else:
    print("tidak ditemukan dokumen yang relevan.")

  return jsonify({
    "query": query,
    "total_results": len(results),
    "results": results
  })

if __name__ == '__main__':
  app.run(debug=True, port=8000)