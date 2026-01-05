from flask import Flask, jsonify, request
from flask_cors import CORS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

DOCUMENTS = [
  {
      "id": 1,
      "title": "Kajian tentang Pengelolaan Sampah di Indonesia",
      "snippet": "Meningkatnya jumlah penduduk, tingkat konsumsi masyarakat, dan kemajuan teknologi akan meningkatkan jumlah timbulan sampah. Sampah yang belum terkelola akan menimbulkan banyak masalah seperti; menjadi sumber penyakit, tercemarnya lingkungan, banjir, dan meningkatnya kebutuhan lahan untuk menimbun sampah. Paradigma lama pengelolaan sampah dengan sistem kumpul-angkut-buang hingga saat ini masih diterapkan oleh masyarakat. Penelitian ini merupakan penelitian studi literatur yang mengidentifikasi dan menganalisis penelitian-penelitian terdahulu tentang pengelolaan sampah melalui tahapan pengumpulan dan analisis 36 jurnal terkait yang diperoleh melalui penelusuran web scholar.google.co.id dan elsevier.com. Hasil penelitian menunjukkan bahwa regulasi sampah di Indonesia masih lemah, partisipasi masyarakat dipengaruhi faktor internal dan eksternal, serta program pengelolaan yang tepat adalah berbasis masyarakat melalui komposting, daur ulang, dan bank sampah."
  },
  {
      "id": 2,
      "title": "Pengelolaan Sampah Rumah Tangga 3R Berbasis Masyarakat",
      "snippet": "Peningkatan jumlah penduduk dan laju pertumbuhan industri akan memberikan dampak pada jumlah sampah yang dihasilkan antara lain sampah plastik, kertas, produk kemasan yang mengandung B3 (Bahan Beracun Berbahaya). Jumlah dan jenis sampah sangat tergantung dari gaya hidup dan jenis material yang kita konsumsi. Berdasarkan UU No. 18 2008, Pengelolaan Sampah Terpadu Berbasis Masyarakat adalah suatu pendekatan pengelolaan sampah yang didasarkan pada kebutuhan dan permintaan masyarakat, direncanakan, dilaksanakan, dikontrol dan dievaluasi bersama masyarakat. Pemerintah dan lembaga lainnya berperan sebagai motivator dan fasilitator untuk memberikan dorongan agar masyarakat siap mencari jalan keluar terhadap persoalan sampah yang mereka hadapi."
  },
  {
      "id": 3,
      "title": "Pengelolaan Sampah dengan Cara Menjadikannya Kompos",
      "snippet": "Solid waste disposal activity is a continuous activity, therefore a solid waste management system is needed. Management of urban solid waste has some difficulties in collecting the solid wastes and finding safe area to disposal them. Composting is needed to reduce its volume. Composting is a biological process and a special process because the raw material, the place, and the method can be done by anyone and wherever. Factors influencing composting are sorting, size, nutrients (C/N ratio), and the moisture of raw material. Effective microorganism 4 (EM4) can be used for composting because it can accelerate the decomposition process of organic solid waste. The result of fermentation process is named bokashi and the compost is useful for kinds of plants."
  },
  {
      "id": 4,
      "title": "Pengelolaan Sampah Desa Gudang Tengah Melalui Manajemen Bank Sampah",
      "snippet": "Bank sampah berdiri karena adanya keprihatinan masyarakat akan lingkungan hidup yang semakin lama semakin dipenuhi dengan sampah baik organik maupun anorganik. Sampah yang semakin banyak tentu akan menimbulkan banyak masalah, sehingga memerlukan pengolahan seperti membuat sampah menjadi bahan yang berguna. Pengelolaan sampah dengan sistem bank sampah ini diharapkan mampu membantu pemerintah dalam menangani sampah dan meningkatkan ekonomi masyarakat. Bank sampah adalah suatu tempat yang digunakan untuk mengumpulkan sampah yang sudah dipilah-pilah. Hasil dari pengumpulan sampah yang sudah dipilah akan disetorkan ke tempat pembuatan kerajinan dari sampah atau ke tempat pengepul sampah. Bank sampah dikelola menggunakan sistem seperti perbankkan yang dilakukan oleh petugas sukarelawan."
  },
  {
      "id": 5,
      "title": "Kebijakan Pemerintah dalam Pengelolaan Sampah Domestik",
      "snippet": "Artikel ini membahas tentang kebijakan pemerintah dalam pengelolaan sampah domestik. Penelitian ini mengevaluasi kebijakan tersebut untuk mengetahui perubahan kualitas lingkungan dan masyarakat akibat implementasi kebijakan pengelolaan sampah di berbagai daerah. Studi ini menyoroti pentingnya instrumen sosial dan kerangka hukum dalam penanganan sampah, serta bagaimana lingkungan yang dibangun berhubungan erat dengan kesehatan publik. Melalui evaluasi ini, diharapkan ditemukan model kebijakan yang lebih efektif untuk menekan jumlah timbulan sampah domestik yang terus meningkat."
  },
  {
      "id": 6,
      "title": "Pengelolaan Sampah Rumah Tangga di Kecamatan Daha Selatan",
      "snippet": "Pembuangan sampah rumah tangga secara sembarangan di sekitar rumah ataupun ke sungai telah menjadi kebiasaan sebagian masyarakat di Kecamatan Daha Selatan, sehingga menimbulkan beberapa penyakit yang berbasis lingkungan serta mencemari Sungai Negara. Penelitian analitik observasional ini bertujuan untuk mengkaji pengelolaan sampah rumah tangga dan faktor-faktor yang berkorelasi. Hasilnya didapatkan rata-rata sampah rumah tangga yang dihasilkan sebanyak 1,46 liter/orang/hari, yang terdiri dari 47% sampah organik, 15% kertas, 22% plastik, serta 16% logam. Pengelolaan sampah belum dilaksanakan secara optimal dan dipengaruhi oleh tingkat pendidikan, tingkat pendapatan, perilaku terhadap kebersihan lingkungan, serta pengetahuan tentang peraturan daerah."
  },
  {
      "id": 7,
      "title": "Perilaku Membuang Sampah Makanan dan Pengelolaan Sampah Makanan di Berbagai Negara: Review",
      "snippet": "Dalam beberapa tahun terakhir, sampah makanan menjadi salah satu isu global yang dapat menimbulkan masalah bagi rantai penyediaan makanan dan pelestarian lingkungan. Salah satu kontributor utama adalah sektor rumah tangga. Tujuan studi ini adalah memberikan tinjauan terhadap berbagai studi tentang food waste behavior, yaitu perilaku seseorang terkait sampah makanan dan konsep pengelolaan sampah makanan pada sektor rumah tangga yang dapat diterapkan di Indonesia berdasarkan implementasi di beberapa negara. Pendekatan yang diulas meliputi psikologi perilaku, keadaan sosio-demografi, serta rutinitas dan praktik terkait perencanaan makanan."
  },
  {
      "id": 8,
      "title": "Analisis Pengelolaan Sampah Padat di Kecamatan Banuhampu Kabupaten Agam",
      "snippet": "Pencemaran lingkungan menyebabkan meningkatnya penyebaran penyakit, mengurangi estetika lingkungan, dan berdampak pada pemanasan global. Di Kecamatan Banuhampu sebagian besar sampah masih dibuang sembarangan yang berpotensi merusak lingkungan sekitar. Hasil penelitian menunjukkan belum adanya perencanaan khusus dalam pengelolaan sampah karena tidak adanya tempat pengelolaan sampah. Meskipun di daerah pedesaan telah ada masyarakat yang mengelola sampah dengan membuat kompos, sebagian besar sampah masih dibuang sembarangan. Diperlukan perwakilan BPLH untuk memanajemen pengelolaan sampah di Kecamatan Banuhampu dan pembuatan peraturan daerah yang tegas."
  },
  {
      "id": 9,
      "title": "Diktat Kuliah TL-3104: Pengelolaan Sampah",
      "snippet": "Diktat ini merupakan bahan kuliah bagi mahasiswa Teknik Lingkungan ITB yang berisi kumpulan pengalaman dan informasi dalam pengelolaan sampah di Indonesia, dilengkapi dengan bahan dari literatur terkait. Materi mencakup aspek teknis operasional pengelolaan sampah perkotaan, konsep daur ulang secara langsung (direct recycling) dan tidak langsung (indirect recycling), serta penanganan akhir sampah melalui landfilling atau insinerasi. Ditekankan bahwa landfilling atau insinerasi digunakan sebagai upaya terakhir untuk menangani limbah yang sudah tidak memiliki nilai lagi untuk didaur ulang."
  },
  {
      "id": 10,
      "title": "Peran Bank Sampah Induk dalam Pengelolaan Sampah Kota Medan",
      "snippet": "Bank sampah memberikan solusi yang mampu menghasilkan keuntungan tidak hanya lingkungan menjadi bersih tapi juga dapat meningkatkan nilai ekonomi dan memberdayakan masyarakat. Penelitian ini bertujuan untuk mengetahui mekanisme bank sampah induk berbasis masyarakat (Bank Sampah Induk Sicanang) dari segi layanan dan konsep berkelanjutan. Mekanisme pengelolaan di BSIS adalah masyarakat memilah sampah dan menabung di bank sampah binaan. Hadirnya BSIS dapat meningkatkan nilai perekonomian masyarakat dan memunculkan kesadaran terhadap pengelolaan sampah yang berwawasan lingkungan. Jumlah sampah yang dikelola mencapai 208,6 kg/hari, dengan dukungan peran serta sektor swasta."
  },
  {
    "id": 11, 
    "title": "Pentingnya Literasi Keuangan bagi Pengelolaan Keuangan Pribadi", 
    "snippet": "Literasi keuangan merupakan kebutuhan dasar bagi setiap orang agar terhindar dari masalah keuangan. Kesulitan keuangan bukan hanya fungsi dari pendapatan semata (rendahnya pendapatan), kesulitan keuangan juga dapat muncul jika terjadi kesalahan dalam pengelolaan keuangan (miss-management) seperti kesalahan penggunaan kredit, dan tidak adanya perencanaan keuangan. Literasi keuangan (financial literacy) yang kian mendapatkan perhatian di banyak negara maju semakin menyadarkan betapa kepada kita betapa pentingnya tingkat 'melek' keuangan. Di beberapa negara, literasi keuangan bahkan sudah dicanangkan menjadi program nasional. Hasil riset secara umum menunjukkan bahwa masih terjadi tingkat literasi keuangan yang rendah di negara-negara maju dan terlebih lagi di negara-negara sedang berkembang termasuk Indonesia. Kondisi ini merupakan problem yang cukup serius mengingat literasi keuangan berpengaruh positif terhadap inklusi dan perilaku keuangan."
  },
  {
    "id": 12, 
    "title": "Pengelolaan Hutan dalam Mengatasi Alih Fungsi Lahan Hutan di Wilayah Kabupaten Subang", 
    "snippet": "Arahan pembinaan hutan dan arahan pengawasan hutan disusun berdasarkan konsep partisipatif. Arahan pembinaan hutan secara umum meliputi program rehabilitasi hutan, sosialisasi pembinaan dan penghijauan kepada masyarakat, penegasan sanksi bagi perambah hutan, membentuk pola enclave pada permukiman dalam kawasan hutan (khususnya hutan lindung), pemberdayaan masyarakat Kabupaten Subang dalam kegiatan pengelolaan hutan. Sedangkan, pada arahan pengawasan hutan dilakukan peningkatan alat dan sarana pengamanan hutan meliputi senjata api, alat komunikasi, alat navigasi, alat pemadam kebakaran, alat penyelamatan, kendaraan operasional, pos jaga dan pondok kerja. Penambahan alat dan sarana pengamanan hutan ini dilakukan pada dua Kesatuan Pengelolaan Hutan (KPH) yaitu KPH Purwakarta dan KPH Bandung Utara, dimana kawasan hutan di Kabupaten Subang termasuk kedalamnya."
  },
  {
    "id": 13, 
    "title": "Dampak Pengelolaan Sampah Medis Dihubungkan dengan Undang-Undang No 36 Tahun 2009 tentang Kesehatan dan Undang-Undang No. 32 Tahun 2009 tentang Perlindungan dan Pengelolaan Lingkungan Hidup", 
    "snippet": "Pengelolaan limbah medis merupakan bagian dari kegiatan penyehatan lingkungan di Rumah Sakit yang bertujuan untuk melindungi masyarakat dari bahaya pencemaran lingkungan yang bersumber dari limbah Rumah Sakit dan upaya penanggulangan penyebaran penyakit. Tiap jenis limbah medis memiliki cara penanganannya sendiri-sendiri. Apabila tidak dilakukan dengan prosedur yang sesuai maka akibatnya akan berdampak lebih parah Sampah atau limbah medis adalah hasil buangan dari suatu aktivitas medis. Limbah medis ini mengandung berbagai macam limbah medis yang berbahaya bagi kesehatan manusia bila tidak diolah dengan benar, dan penyimpanan menjadi pilihan terakhir jika limbah tidak dapat langsung diolah. Limbah medis kebanyakan sudah terkontaminasi dengan bakteri, virus, racun dan bahan radioaktif yang berbahaya bagi manusia dan mahluk lain disekitar lingkungannya. Dampak negatif limbah medis terhadap masyarakat dan lingkungannya terjadi akibat pengelolaan yang kurang baik. Dampak yang terjadi dari limbah medis tersebut dapat menimbulkan patogen yang dapat berakibat buruk terhadap manusia dan lingkungannya."
  },
  {
    "id": 14, 
    "title": "Sistem Pemeliharaan Anjing dan Tingkat Pemahaman Masyarakat terhadap Penyakit Rabies di Kabupaten Bangli, Bali", 
    "snippet": "Rabies adalah penyakit zoonosis yang bersifat mematikan. Penyakit ini menyerang sistem saraf pusat atau encephalitis. Penelitian ini bertujuan untuk mengetahui persentase dan hubungan antara faktor-faktor yang memengaruhi sistem pemeliharaan dan tingkat pemahaman masyarakat terhadap penyakit rabies di Kabupaten Bangli, Bali. Jumlah responden yang diambil sebanyak 140, tersebar di 14 desa yang belum pernah dilaporkan terjadi kasus rabies. Data hasil wawancara berdasarkan kuisioner dianalisis menggunakan analisis deskriptif kuantitatif dan dendrogram. Hasil penelitian menunjukkan bahwa sistem pemeliharaan anjing yang baik di Kabupaten Bangli berhubungan dengan kondisi pemeliharaan anjing (100%); kesadaran memberikan pakan (100%); jumlah pemberian pakan yang lebih dari satu kali (91,4%); status vaksinasi rabies (83,6%); tidak memelihara hewan penular rabies (HPR) selain anjing (kucing) (75,7%); status pemeriksaan kesehatan (67,1%); dan jumlah anjing yang dipelihara tidak lebih dari satu ekor (55,7%). Sistem pemeliharaan anjing yang buruk berhubungan dengan jenis pakan yang diberikan (100%); berkontak dengan anjing lainnya (80%); dan sistem pemeliharaan anjing dengan cara dilepas (73,6%). Tingkat pemahaman masyarakat Kabupaten Bangli yang baik berhubungan dengan mobilitas anjing (88,6%); pemahaman mengenai bahaya rabies (79,3%); asal anjing (79,3%); pengetahuan mengenai ciri-ciri rabies (74,3%); dan status desa bebas rabies yang masih dipertahankan (78,6%). Tingkat pemahaman masyarakat yang buruk berhubungan dengan belum adanya aturan desa maupun aturan adat yang berkaitan dengan penyakit rabies (100%); kurangnya pastisipasi masyarakat dalam program penyuluhan (62,1%); dan cara memperoleh anjing (52,1%). Berdasarkan hasil penelitian dapat disimpulkan bahwa sistem pemeliharaan anjing dan tingkat pemahaman masyarakat mengenai penyakit rabies di Kabupaten Bangli tergolong baik."},
  {
    "id": 15,
    "title": "Pengelolaan Sampah Plastik untuk Mitigasi Bencana Lingkungan",
    "snippet": "Seiring berkembangnya teknologi, industri dan jumlah penduduk, penggunaan plastik dan barang-barang berbahan dasar plastik semakin meningkat. Plastik banyak digunakan dalam berbagai keperluan karena sifatnya yang ringan, kuat, tidak mudah pecah, fleksibel, mudah dibentuk, tahan karat, mudah diberi warna, isolator panas dan listrik yang baik serta harganya yang terjangkau. Berdasarkan hasil studi, Indonesia adalah negara penghasil sampah plastik nomor dua di dunia setelah Tiongkok, yang berkontribusi atas 3,2 juta ton sampah di lautan setiap tahunnya. Hal itu membuat Indonesia jadi penghasil sampah plastik terbanyak di Asia Tenggara. Diperlukan waktu puluhan hingga ratusan tahun untuk terdegradasinya sampah plastik tersebut. Banyaknya sampah plastik ini akan berdampak negatif terhadap kesehatan dan lingkungan yang akhirnya dapat menimbulkan bencana, antara lain emisi gas rumah kaca ke atmosfir serta banjir. Berdasarkan hal tersebut, perlu dilakukan pengelolaan sampah plastik untuk mitigasi bencana lingkungan. Mitigasi dapat dilakukan dengan pendekatan teknologi; sosial, ekonomi budaya; serta kelembagaan. Pendekatan teknologi dapat dilakukan misalnya penggunaan pirolisis, penggunaan hydro thermal, ataupun penggunaan bahan baku yang ramah lingkungan. Pelibatan masyarakat, dan sosialisasi merupakan contoh pendekatan secara sosial dan budaya dan pendekatan ekonomi dapat dilakukan dengan penerapan ekonomi sirkuler. Untuk pendekatan kelembagaan dilakukan dengan melibatkan pemerintah pusat maupun daerah dalam implementasi kebijakan atau peraturan-peraturan yang ada serta penyiapan peraturan baru terkait pengurangan sampah plastik."
  },
  {
    "id": 16,
    "title": "Pengaruh Pengetahuan tentang Sampah dan Ketersediaan Sarana Prasarana terhadap Perilaku Ibu Membuang Sampah yang Berpotensi Bencana Banjir di Daerah Aliran Sungai Deli Kota Medan",
    "snippet": "Hasil survei awal menunjukkan bahwa pengetahuan masyarakat dalam membuang sampah jauh belum memadai dan sarana dan prasarana pengelolaan sampah yang memadai belum tersedia. Hal ini mungkin dapat membuat perilaku buruk dari ibu dalam membuang sampah jauh di sungai Deli yang berpotensi untuk menimbulkan banjir di Kota Medan. Tujuan dari penelitian explanatory ini adalah untuk menganalisis pengaruh pengetahuan ibu tentang manfaat, efek, pencegahan dan ketersediaan sarana infrastruktur yang terkait dengan membuang potensi sampah menyebabkan banjir di Sungai Deli Kota Medan. Populasi penelitian ini adalah 14.956 ibu rumah tangga yang tinggal di sepanjang tepi Sungai Deli di Medan dan 99 dari mereka dipilih menjadi sampel untuk penelitian ini dengan menggunakan rumus Slovin. Data yang diperoleh dianalisis melalui uji regresi linier berganda pada a=95%. Hasil penelitian ini menunjukkan bahwa pengetahuan masyarakat dalam merespon manfaat, efek, dan pencegahan melalui aksi pengelolaan sampah dan ketersediaan sarana prasarana yang memiliki pengaruh pada sikap ibu dalam membuang sampah di daerah aliran sungai pada Sungai Deli yang berpotensial menimbulkan banjir. Pemerintah Kota Medan dan instansi terkait disarankan untuk menerapkan pengumpul sampah. Pemerintah Kota Medan harus merencanakan peraturan mengenai alokasi dana untuk mengeruk aliran sungai Deli, jadwal kegiatan untuk sekali dalam dua tahun dan memberdayakan komponen masyarakat (puskesmas, aparat desa / promotor lingkungan dan LSM) dan masyarakat dalam mengendalikan bencana banjir."
  },
  {
    "id": 17,
    "title": "Analisis Kesiapsiagaan Bencana Banjir di Jakarta",
    "snippet": "Indonesia merupakan negara yang rawan akan bencana baik bencana alam maupun non alam. Bencana merupakan sebuah peristiwa yang mengancam dan mengganggu kehidupan dan penghidupan masyarakat. Banjir merupakan luapan air yang tidak dapat ditampung sungai, banjir juga merupakan sebuah bencana karena mengganggu aktivitas yang masyarakat. DKI Jakarta memiliki resiko rentan bencana banjir yang tegolong tinggi. Oleh karenanya perlu dilakukan upaya untuk menanggulangi bencana banjir tersebut. Hal ini berkaitan dengan kesiapsiagaan bencana banjir di DKI Jakarta, oleh karenanya perlu ada kegiatan untuk pemenuhan 5 paramaeter kesiapsiagaan yang nantinya dapat dinilai bahwasannya DKI Jakarta sudah siap terhadap bencana banjir."
  },
  {
    "id": 18,
    "title": "Analisis Penyebab Banjir di Kota Padang",
    "snippet": "Tujuan penelitian ini adalah untuk mengetahui persebaran banjir di Kota Samarinda, mengindentifikasi penyebab banjir di Kota Samarinda, dan mengindentifikasi dampak banjir terhadap masyarakat Kota Samarinda. Kota Samarinda adalah daerah yang rawanterhadap bencana banjir. Dimana penyebab banjir permasalahan banjir di Kota Samarinda terjadi akibat berlebihnya limpasan permukaan dan tidak tertampungnya limpasan tersebut dalam badan sungai sehingga air meluap. Ada dua faktor yang menyebabkan banjir di Kota Samarinda yang pertama, Faktor alam seperti tingginya curah hujan, topografi wilayah, pasang surut air sungai Mahakam, dan lain-lain. Dan yang kedua, adalah manusia, utamanya bersumber pada unsur pertumbuhan penduduk akan diikuti peningkatan kebutuhan infrastruktur, pemukiman, sarana air bersih, pendidkan, serta layanan masyarakat lainnya. Selain itu pertumbuhan penduduk akan diikuti juga kebutuhan lahan usaha untuk pertanian, perkebunan, maupun industry. Sumber genangan (banjir) di Kota Samarinda khususnya yang dampaknya pada aktivitas masyarakat dapat dibedakan menjadi 3 macam, yaitu, akibat pasang sungai Mahakam.yang pertama banjir kiriman, yang kedua banjir lokal, dan yang ketiga adalah banjir akibat pasang sungai Mahakam. ."
  },
  {
    "id": 19,
    "title": "Analisis Penyebab Banjir di Kota Samarinda",
    "snippet": "Tujuan penelitian ini adalah untuk mengetahui persebaran banjir di Kota Samarinda, mengindentifikasi penyebab banjir di Kota Samarinda, dan mengindentifikasi dampak banjir terhadap masyarakat Kota Samarinda. Kota Samarinda adalah daerah yang rawan terhadap bencana banjir. Dimana penyebab banjir permasalahan banjir di Kota Samarinda terjadi akibat berlebihnya limpasan permukaan dan tidak tertampungnya limpasan tersebut dalam badan sungai sehingga air meluap. Ada dua faktor yang menyebabkan banjir di Kota Samarinda yang pertama, Faktor alam seperti tingginya curah hujan, topografi wilayah, pasang surut air sungai Mahakam, dan lain-lain. Dan yang kedua, adalah manusia, utamanya bersumber pada unsur pertumbuhan penduduk akan diikuti peningkatan kebutuhan infrastruktur, pemukiman, sarana air bersih, pendidkan, serta layanan masyarakat lainnya. Selain itu pertumbuhan penduduk akan diikuti juga kebutuhan lahan usaha untuk pertanian, perkebunan, maupun industry. Sumber genangan (banjir) di Kota Samarinda khususnya yang dampaknya pada aktivitas masyarakat dapat dibedakan menjadi 3 macam, yaitu, akibat pasang sungai Mahakam.yang pertama banjir kiriman, yang kedua banjir lokal, dan yang ketiga adalah banjir akibat pasang sungai Mahakam."
  },
  {
    "id": 20,
    "title": "Perancangan Sistem Informasi Evaluasi Kinerja Dosen Berbasis Website (Studi Kasus STMIK Primakara)",
    "snippet": "Pada kampus STMIK Primakara masih memiliki kendala atau permasalahan dalam proses kegiatan evaluasi kinerja dosen khususnya pada pengelolaan data penelitian, pengabdian dan penunjang. Pengelolaan dilakukan secara manual, karena belum adanya sistem informasi dalam pengelolaan data tersebut, membuat proses pelaporan menjadi terlambat dan tidak jarang lupa untuk melakukan penyetoran data kegiatan yang telah diikuti selama satu semester. Tujuan penelitian ini dapat membantu proses evaluasi kinerja dosen khususnya pada kegiatan penelitian, pengabdian dan penunjang. Metode yang digunakan dalam penelitian ini yaitu metode prototype, dimana peneliti menggunakan metode pengumpulan data dengan melakukan wawancara kepada bagian LPPM, HRD, dan Kaprodi, selain itu juga dengan melakukan studi literatur. Hasil dari penelitian ini yaitu dosen dapat melakukan input data penelitian, pengabdian dan juga penunjang secara tersistem, untuk team reviewer memberikan penilaian terhadap penelitian dan pengabdian yang diajukan, sedangkan bagian LPPM melakukan approved dan rejected terhadap penelitian dan pengabdian yang diajukan, dan untuk HRD dapat melakukan validasi data penunjang yang telah diajukan dosen. Dalam membuat perancangan sistem informasi ini peneliti menggunakan framework VueJS dengan template metronic."
  }
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
  app.run(debug=True, port=5501)