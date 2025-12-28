from flask import Flask, jsonify
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVektorizer

app = Flask(__name__)
CORS(app)

DOCUMENTS = [
  {"id": 1, "title": "This is the first document.", "snippet": "...."},
  {"id": 2, "title": "This document is the second document", "snippet": "...."},
  {"id": 3, "title": "And this is the third one", "snippet": "...."},
  {"id": 4, "title": "Is this the first document?", "snippet": "...."},
  {"id": 5, "title": "lorem ipsum dolor st amet", "snippet": "...."},
  {"id": 6, "title": "lorem ipsum dolor st amet", "snippet": "...."},
  {"id": 7, "title": "lorem ipsum dolor st amet", "snippet": "...."},
  {"id": 8, "title": "lorem ipsum dolor st amet", "snippet": "...."},
  {"id": 9, "title": "lorem ipsum dolor st amet", "snippet": "...."},
]

vectorizer = TfidfVektorizer()
X = vectorizer.fit_transform(DOCUMENTS)
vectorizer.get_feature_names_out(['and', 'document', 'first', 'is', 'one', 'second', 'the', 'third', 'this'])

print(X.shape)

@app.route('/api/search', methods=['GET'])
def search_documents():
  return jsonify(DOCUMENTS)

if __name__ == '__main__':
  app.run(debug=True)