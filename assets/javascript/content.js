// content.js

document.addEventListener("DOMContentLoaded", () => {
    const hamburgerIcon = document.getElementById("hamburger");
    const body = document.body;
  
    // Fungsi untuk membuka/tutup sidebar
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
  
    // Mengambil data dokumen dari localStorage
    const documentData = localStorage.getItem('currentDocument');
    
    if (documentData) {
      const doc = JSON.parse(documentData);
      displayDocument(doc);
    } else {
      // Jika tidak ada data, tampilkan pesan error atau redirect
      console.error("Tidak ada data dokumen");
      displayDefaultContent();
    }
  
    // Fungsi untuk menampilkan dokumen
    function displayDocument(doc) {
      // Update judul dokumen
      const documentTitle = document.querySelector('.document-title');
      if (documentTitle) {
        documentTitle.textContent = doc.title;
      }
  
      // Update konten utama
      const mainText = document.querySelector('.main-text');
      if (mainText && doc.content) {
        // Pisahkan konten menjadi paragraf jika ada
        const paragraphs = doc.content.split('\n\n');
        mainText.innerHTML = '';
        
        paragraphs.forEach((para, index) => {
          if (para.trim()) {
            const p = document.createElement('p');
            p.textContent = para;
            mainText.appendChild(p);
            
            // Tambahkan separator setelah paragraf pertama
            if (index === 0 && paragraphs.length > 1) {
              const hr = document.createElement('hr');
              hr.className = 'separator';
              mainText.appendChild(hr);
            }
          }
        });
      } else if (mainText && doc.snippet) {
        // Jika tidak ada content, gunakan snippet
        const paragraphs = doc.snippet.split('\n\n');
        mainText.innerHTML = '';
        
        paragraphs.forEach((para) => {
          if (para.trim()) {
            const p = document.createElement('p');
            p.textContent = para;
            mainText.appendChild(p);
          }
        });
      }
  
      // Update sidebar introduction
      const introductionDiv = document.querySelector('.introduction');
      if (introductionDiv) {
        // Hapus konten lama kecuali h3
        const h3 = introductionDiv.querySelector('h3');
        introductionDiv.innerHTML = '';
        if (h3) {
          introductionDiv.appendChild(h3);
        } else {
          const newH3 = document.createElement('h3');
          newH3.textContent = 'Introduction';
          introductionDiv.appendChild(newH3);
        }
  
        // Tambahkan introduction text
        if (doc.introduction) {
          const introParagraphs = doc.introduction.split('\n\n');
          introParagraphs.forEach(para => {
            if (para.trim()) {
              const p = document.createElement('p');
              p.textContent = para;
              introductionDiv.appendChild(p);
            }
          });
        } else {
          // Fallback: gunakan 200 karakter pertama dari snippet
          const p = document.createElement('p');
          p.textContent = doc.snippet ? doc.snippet.substring(0, 200) + '...' : 'No introduction available.';
          introductionDiv.appendChild(p);
        }
      }
  
      // Update link PDF jika ada
      const pdfButton = document.querySelector('.pdf-button');
      if (pdfButton && doc.pdf_url) {
        pdfButton.href = doc.pdf_url;
        pdfButton.target = '_blank';
      } else if (pdfButton) {
        pdfButton.href = '#';
        pdfButton.addEventListener('click', (e) => {
          e.preventDefault();
          alert('PDF tidak tersedia untuk dokumen ini.');
        });
      }
    }
  
    // Fungsi untuk menampilkan konten default jika tidak ada data
    function displayDefaultContent() {
      const documentTitle = document.querySelector('.document-title');
      if (documentTitle) {
        documentTitle.textContent = 'Dokumen Tidak Ditemukan';
      }
  
      const mainText = document.querySelector('.main-text');
      if (mainText) {
        mainText.innerHTML = '<p>Data dokumen tidak tersedia. Silakan kembali ke halaman pencarian.</p>';
      }
    }
  
    // Event listener untuk sidebar links (opsional)
    const sidebarLinks = document.querySelectorAll('#sidebar-menu a');
    sidebarLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        // Anda bisa menambahkan fungsi untuk load dokumen dari sidebar jika diperlukan
        console.log('Sidebar link clicked:', e.target.textContent);
      });
    });
  });