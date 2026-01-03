from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import os
from PyPDF2 import PdfReader
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import word_tokenize
import joblib

app = Flask(__name__)
CORS(app)

def Preprocess_text(text):
  """Melakukan tokenisasi dan stemming pada teks berbahasa indonesia"""
  factory = StemmerFactory()
  stemmer = factory.create_stemmer()
  tokens = word_tokenize(text.lower())

  #stemming
  stemmed_text = ' '.join([stemmer.stem(token) for token in tokens])
  return stemmed_text

# Fungsi Extraksi PDF
def extract_text_from_pdf(filepath):
  """Ekstrak Teks dari File Pdf """
  text = ""
  try: 
    with open(filepath, 'rb') as file:
      reader = PdfReader(file)
      for page in reader.pages:
        text += page.extract_text() or ""
  except Exception as e:
    print(f"Error Membaca {filepath}: {e}")
    return None
  return text

def extract_abstract_snippet(full_text, max_length=500):
    """Mencari dan mengambil teks Abstract atau Abstrak dari teks penuh."""
    
    # Mencari Abstract Bahasa Inggris
    start_en = full_text.find("Abstract:")
    if start_en != -1:
        start_index = start_en + len("Abstract:")
        # Tentukan akhir dengan mencari penanda umum (misalnya Keywords:) atau baris kosong yang signifikan
        end_en = full_text.find("Keywords:", start_index) 
        
        if end_en != -1:
            abstract_text = full_text[start_index:end_en].strip()
        else:
            abstract_text = full_text[start_index:].strip()
            
        # Jika Abstract ditemukan, bersihkan spasi berlebihan
        # dan batasi panjangnya
        cleaned_snippet = " ".join(abstract_text.split()) 
        return cleaned_snippet[:max_length] + "..."

    # Mencari Abstrak Bahasa Indonesia
    start_id = full_text.lower().find("abstrak:")
    if start_id != -1:
        start_index = start_id + len("abstrak:")
        # Tentukan akhir dengan mencari penanda umum (misalnya Keywords)
        end_id = full_text.lower().find("kata kunci:", start_index)
        
        if end_id != -1:
             # Kita perlu menggunakan index yang sudah lowercase/find() untuk memotong dari teks asli
             abstract_text = full_text[start_index:end_id].strip()
        else:
             abstract_text = full_text[start_index:].strip()
             
        cleaned_snippet = " ".join(abstract_text.split())
        return cleaned_snippet[:max_length] + "..."

    # Jika tidak ditemukan penanda, kembali ke 200 karakter pertama sebagai fallback
    return " ".join(full_text[:500].split()) + "..."

# memuat dan memproses dokumen
DOCUMENTS = []
text_corpus = []

DOCUMENTS_FOLDER = r'E:\File Bisma\project IRE\RepoLibFind\assets\python\document'

if os.path.isdir(DOCUMENTS_FOLDER):
  print(f"[INFO] Memuat dokumen dari folder: {DOCUMENTS_FOLDER}")
  for filename in os.listdir(DOCUMENTS_FOLDER):
    if filename.endswith('.pdf'):
      filepath = os.path.join(DOCUMENTS_FOLDER, filename)
      raw_text = extract_text_from_pdf(filepath)

      if raw_text:
        proccessed_text = Preprocess_text(raw_text)
        raw_snippet = extract_abstract_snippet(raw_text)
        doc_id = len(DOCUMENTS) + 1
        DOCUMENTS.append({
          'id': doc_id,
          'title': filename,
          'snippet': raw_snippet[:200] + "...",
          'processed_text': proccessed_text
        })
        text_corpus.append(proccessed_text)
        print(f"Berhasil memproses: {filename}")

    else: 
      print(f"[ERROR] Folder dokumen tidak ditemukan: {DOCUMENTS_FOLDER}")
    # Tambahkan beberapa data dummy jika tidak ada folder
    DOCUMENTS.append({'id': 0, 'title': 'Dummy Doc 1', 'snippet': 'ini dokumen dummy', 'processed_text': 'ini dokumen dummy'})
    text_corpus.append('ini dokumen dummy')

if text_corpus:
  vectorizer = TfidfVectorizer()
  X = vectorizer.fit_transform(text_corpus)
  features = vectorizer.get_feature_names_out()
  print(f"[INFO] TF-IDF dihitung untuk {len(text_corpus)} dokumen. Jumlah fitur: {len(features)}")
else:
  print("[ERROR] Tidak ada dokumen yang dimuat. Periksa path folder.")

#Fungsi pencarian (API)
@app.route('/api/search', methods=['GET'])
def search_documents():
  query = request.args.get('q')
  if not query:
    return jsonify({"message": "Mohon masukan Quary Pencarian.", "result": []})

  processed_query = Preprocess_text(query)
  print(f"\n[INFO] Query asli: {query}")
  print(f"\n[INFO] Query diproses: {processed_query}")

  if not processed_query:
    return jsonify({"message": "Query tidak valid setelah pemrosesan.", "result": []})
    
  query_vector = vectorizer.transform([processed_query])
  cosine_scores = cosine_similarity(query_vector, X).flatten()

  results = []
  for i, score in enumerate(cosine_scores):
    if score > 0.0:
      doc = DOCUMENTS[i].copy()
      if 'processed_text' in doc:
        del doc['processed_text']

      if'snippet' in doc and len(doc['snippet']) > 500:
        doc['snippet'] = doc['snippet'].encode('utf-8', 'ignore').decode('utf-8')[:500] + "..."
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
  app.run(debug=False)