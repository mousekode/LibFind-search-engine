// script.js

document.addEventListener("DOMContentLoaded", () => {

  const searchButton = document.getElementById("search-button");
  const homeScreen = document.getElementById("home-screen");
  const resultsScreen = document.getElementById("results-screen");
  const searchInput = document.getElementById("search-input");
  const hamburgerIcon = document.getElementById("hamburger");
  const body = document.body;
  // Fungsi untuk menampilkan hasil
  const showResults = () => {
    // 1. Sembunyikan konten utama (Hello Readers)
    homeScreen.style.opacity = "0";
    homeScreen.style.position = "fixed";

    // 2. Tampilkan area hasil pencarian setelah transisi home-screen selesai
    setTimeout(() => {
      homeScreen.classList.add("hidden");
      resultsScreen.classList.remove("hidden");

      // Atur opacity hasil pencarian agar terlihat
      setTimeout(() => {
        resultsScreen.style.opacity = "1";
      }, 10);
    }, 300); // Sesuaikan dengan durasi transisi di CSS (0.3s)

    // 3. Posisikan search-container di bawah header untuk Gambar 1
    const searchContainer = document.querySelector(".search-container");
    searchContainer.style.position = "fixed"; // Gunakan fixed agar tetap di tempat
    searchContainer.style.top = "auto"; // Sesuaikan posisi di bawah header
    searchContainer.style.bottom = "80px"; // Hilangkan posisi bottom
  };

  // Sambung ke connector.js
  const passToConnector = (value) => {
    runQuery(value);
  };

  // Tambahkan event listener untuk tombol
  searchButton.addEventListener("click", showResults);

  // Tambahkan event listener untuk Enter pada input
  searchInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      showResults();
    }
  });

  // --- Inisialisasi Tampilan ---
  // Pastikan hasil pencarian disembunyikan saat load
  resultsScreen.classList.add("hidden");
  resultsScreen.style.opacity = "0";
  //Fungsi membuka sidebar
  const toggleSideBar = () => {
    body.classList.toggle("sidebar-open");
  };

  //Event listener untuk hamburger menu
  if (hamburgerIcon) {
    hamburgerIcon.addEventListener("click", toggleSideBar);
  }
});
