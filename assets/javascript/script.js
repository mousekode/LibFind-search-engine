// script.js

// --- 1. NAVIGASI & PENYIMPANAN ---
document.addEventListener("DOMContentLoaded", () => {
  const searchButton = document.getElementById("search-button");
  const searchContainer = document.querySelector(".search-container");
  const homeScreen = document.getElementById("home-screen");
  const resultsList = document.querySelector(".results-list");
  const resultsScreen = document.getElementById("results-screen");
  const searchInput = document.getElementById("search-input");
  const body = document.body;

  // --- 2. FUNGSI UNTUK MENAMPILKAN HASIL (BAGIAN YANG KAMU TANYAKAN) ---

  const renderResults = (documents) => {
    resultsList.innerHTML = "";

    if (documents.length === 0) {
      resultsList.innerHTML =
        '<div class="result-item" style="text-align: center;">Tidak ada dokumen yang ditemukan.</div>';
      return;
    }

    // Menampilkan maksimal 5 hasil teratas
    documents.slice(0, 5).forEach((doc, index) => {
      const resultItem = document.createElement("div");
      resultItem.className = "result-item";
      resultItem.style.cursor = "pointer";

      // Path PDF diambil dari JSON (contoh: "python/document/namafile.pdf")
      const pdfPath = doc.doc_path || "#";

      resultItem.innerHTML = `
          <p class="number">${index + 1}.</p>
          <div class="content">
            <a href="${pdfPath}" target="_blank" class="title-link" style="text-decoration:none">${
        doc.title
      }</a>
            <p class="snippet">${doc.snippet.substring(0, 260)}...</p>
          </div>
        `;

      const titleLink = resultItem.querySelector(".title-link");

      // Click logic: Opens the PDF in a new tab
      titleLink.addEventListener("click", (e) => {
        if (pdfPath === "#") {
          e.preventDefault();
          alert("File PDF tidak ditemukan.");
        }
        e.stopPropagation();
      });

      // Event Klik Kotak: Pindah ke halaman PDF
      resultItem.addEventListener("click", () => {
        window.open(pdfPath, "_blank");
      });

      resultsList.appendChild(resultItem);
    });
  };

  // --- 3. FUNGSI UTAMA PENCARIAN (FETCH KE BACKEND) ---

  const showResults = async () => {
    const query = searchInput.value;

    if (!query.trim()) {
      alert("Mohon masukkan kata kunci pencarian.");
      return;
    }

    // Efek Transisi UI
    homeScreen.style.opacity = "0";
    setTimeout(() => {
      homeScreen.classList.add("hidden");
      resultsScreen.classList.remove("hidden");
      setTimeout(() => {
        resultsScreen.style.opacity = "1";
      }, 50);
    }, 300);

    // Styling Search Container (Pindah ke atas)
    searchContainer.style.position = "fixed";
    searchContainer.style.top = "auto";
    searchContainer.style.bottom = "80px";

    const encodedQuery = encodeURIComponent(query);
    const backendUrl = `http://127.0.0.1:5000/api/search?q=${encodedQuery}`;

    try {
      const response = await fetch(backendUrl);
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();

      if (data && data.results) {
        renderResults(data.results);
      } else {
        renderResults([]);
      }
    } catch (error) {
      console.error("Gagal mengambil data:", error);
      resultsList.innerHTML =
        '<div class="result-item">Gagal Memuat Hasil. Pastikan Python (Flask) sudah jalan.</div>';
    }
  };

  // --- 4. EVENT LISTENERS (INPUT) ---

  searchButton.addEventListener("click", showResults);

  searchInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") showResults();
  });

  // Inisialisasi awal
  resultsScreen.classList.add("hidden");
});
