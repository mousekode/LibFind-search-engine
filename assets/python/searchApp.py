from flask import Flask, jsonify, request
from flask import send_from_directory
from flask_cors import CORS
import nltk
from  nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import pandas as pd
import numpy as np
import json
from pathlib import Path
import os

app = Flask(__name__)
CORS(app)

indonesian_stopwords = set(stopwords.words('indonesian'))
# bapak file / skrip ini berada di direktori apa?
script_dir = Path(__file__).parent
doc_path = script_dir / 'ekstrak.json'

with open(doc_path, 'r', encoding='utf-8') as f:
  DOCUMENTS = json.load(f)

factory = StemmerFactory()
stemmer = factory.create_stemmer()

def custom_tokenizer(text):
  #Tokenisasi default TfidfVectorizer
  tokens = TfidfVectorizer().build_tokenizer()(text)
  #Stemming setiap token
  stemmed_tokens = [stemmer.stem(token) for token in tokens]
  return stemmed_tokens

text_corpus = [doc['title'] + " " + doc['snippet'] for doc in DOCUMENTS]

indonesian_stopwords = stopwords.words('indonesian')
tambahan_stopwords = ['baiknya', 'berkali', 'kali', 'kurangnya', 'mata', 'olah', 'sekurang', 'setidak', 'tama', 'tidaknya']
final_stopwords = indonesian_stopwords + tambahan_stopwords
vectorizer = TfidfVectorizer(stop_words=final_stopwords)
X = vectorizer.fit_transform(text_corpus)

@app.route('/api/search', methods=['GET'])
def search_documents():
  query = request.args.get('q', '')
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
    for doc in results [:5]:
      print(f"[{doc['ranking']}] {doc['title'][:50]}... | Skor: {doc['relevansi']}")
  else:
    print("tidak ditemukan dokumen yang relevan.")

  return jsonify({
    "query": query,
    "total_results": len(results),
    "results": results
  })

  # Add this route to your Flask app
@app.route('/assets/python/document/<path:filename>')
def serve_pdf(filename):
    # This points to the folder where the PDFs actually live
    pdf_directory = script_dir / 'document'
    return send_from_directory(pdf_directory, filename)

# Cara untuk tidak menggunakan route statis Flask default
# Agar tidak 404 ketika refresh halaman
# Route for the main page
@app.route('/')
@app.route('/index.html')
def serve_index():
    # Looks for index.html in the folder two levels up from searchApp.py
    return send_from_directory('../../', 'index.html')

# Route for the content page
@app.route('/content.html')
def serve_content():
    return send_from_directory('../../', 'content.html')

# General route for all other assets (CSS, JS, Images)
@app.route('/assets/<path:path>')
def serve_assets(path):
    # Points to the 'assets' folder in your project root
    return send_from_directory('../../assets', path)

if __name__ == '__main__':
  app.run(debug=True)
