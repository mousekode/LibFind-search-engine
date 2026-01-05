// script.js

document.addEventListener("DOMContentLoaded", () => {
  const searchButton = document.getElementById("search-button");
  const searchContainer = document.querySelector(".search-container");
  const homeScreen = document.getElementById("home-screen");
  const resultsList = document.querySelector(".results-list");
  const resultsScreen = document.getElementById("results-screen");
  const searchInput = document.getElementById("search-input");
  const hamburgerIcon = document.getElementById("hamburger");
  const body = document.body;

  // Fungsi untuk menampilkan hasil

  const showResults = async () => {
    // 2. Tampilkan area hasil pencarian setelah transisi home-screen selesai

    // Atur opacity hasil pencarian agar terlihat
    setTimeout(() => {
      homeScreen.classList.add("hidden");
      setTimeout(() => {
        resultsScreen.style.opacity = "1";
        resultsScreen.classList.remove("hidden");
      }, 0);
    }, 300); // Sesuaikan dengan durasi transisi di CSS (0.3s)

    const query = searchInput.value;

    if (!query.trim()) {
      resultsList.innerHTML =
        '<div class="result-item" style="text-align: center; color: #ff6666;">Mohon Masukkan Kata Kunci Pencarian.</div>';
      console.warn("input pencarian kosong.");
      return;
    }
    const encodedQuery = encodeURIComponent(query);
    const backendUrl = `http://127.0.0.1:5501/api/search?q=${encodedQuery}`;

    // 1. Sembunyikan konten utama (Hello Readers)
    resultsScreen.style.opacity = "0";
    homeScreen.style.opacity = "0";
    homeScreen.style.position = "fixed";

    //mencoba ambil data dari backend
    try {
      const response = await fetch(backendUrl);
      if (!response.ok) {
        throw new Error(`HTTP error! status: &{response.status}`);
      }
      const data = await response.json();

      if (data && data.results) {
        renderResults(data.results);
      } else {
        renderResults([]);
      }
    } catch (error) {
      console.error("Gagal mengambil data dari backend:", error);
      resultsList.innerHTML =
        '<div class="result-item">Gagal Memuat Hasil. Cek koneksi BackEnd Anda.</div>';
    }

    // 3. Posisikan search-container di bawah header untuk Gambar 1
    searchContainer.style.position = "fixed"; // Gunakan fixed agar tetap di tempat
    searchContainer.style.top = "auto"; // Sesuaikan posisi di bawah header
    searchContainer.style.bottom = "80px"; // Hilangkan posisi bottom
  };

  // Inisialisasi Tampilan
  resultsScreen.classList.add("hidden");

  //Definisikan data Menu dalam betuk array objek

  
  // Fungsi membuka sidebar
  const toggleSideBar = () => {
    body.classList.toggle("sidebar-open");
  };

  // Fungsi untuk menutup sidebar
  const closeSidebar = () => {
    body.classList.remove("sidebar-open");
  };

  // Event listener untuk hamburger menu
  if (hamburgerIcon) {
    hamburgerIcon.addEventListener("click", toggleSideBar);
  }

  // Event listener untuk menutup sidebar saat klik overlay
  body.addEventListener("click", (e) => {
    if (body.classList.contains("sidebar-open")) {
      // Jika klik di luar sidebar dan bukan hamburger icon
      const sidebar = document.getElementById("sidebar-menu");
      if (!sidebar.contains(e.target) && e.target !== hamburgerIcon) {
        closeSidebar();
      }
    }
  });

  // Fungsi untuk menyimpan data dokumen ke localStorage
  const saveDocumentData = (doc) => {
    localStorage.setItem("currentDocument", JSON.stringify(doc));
  };

  // Fungsi untuk navigasi ke halaman content
  const navigateToContent = (doc) => {
    saveDocumentData(doc);
    window.location.href = "content.html";
  };
  // Fungsi untuk menempelkan data ke HTML
  const renderResults = (documents) => {
    resultsList.innerHTML = "";

    if (documents.length === 0) {
      resultsList.innerHTML =
        '<div class="result-item">Tidak ada dokumen yang ditemukan.</div>';
      return;
    }

    documents.slice(0, 5).forEach((doc, index) => {
      const textLimit = 260;
      const snippet =
        doc.snippet.length > textLimit
          ? doc.snippet.substring(0, textLimit) + "..."
          : doc.snippet;

      // Membuat elemen result-item
      const resultItem = document.createElement("div");
      resultItem.className = "result-item";
      resultItem.style.cursor = "pointer";

      resultItem.innerHTML = `
        <p class="number">${index + 1}.</p>
        <div class="content">
          <a href="#" class="title">${doc.title}</a>
          <p class="snippet">${snippet}</p>
        </div>
      `;

      // Event listener untuk klik pada seluruh item
      resultItem.addEventListener("click", (e) => {
        e.preventDefault();
        navigateToContent(doc);
      });

      resultsList.appendChild(resultItem);
    });
  };

  // Tambahkan event listener untuk tombol
  searchButton.addEventListener("click", showResults);

  // Tambahkan event listener untuk Enter pada input
  searchInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      showResults();
    }
  });
});

