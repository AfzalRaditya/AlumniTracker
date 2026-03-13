# 🎓 Alumni Tracker System (OSINT Engine)

Sistem pelacakan alumni otomatis yang menggunakan teknik **Open Source Intelligence (OSINT)** untuk memvalidasi keberadaan dan profil profesional alumni melalui sumber data publik (OpenAlex API & Web Indexing). Proyek ini dikembangkan untuk memenuhi tugas matakuliah **Rekayasa Kebutuhan**.

## 🚀 Fitur Utama
- **Hybrid Scraping Engine**: Menggabungkan data akademik dari OpenAlex API dan indeks web global.
- **Weighted Scoring Logic**: Menghitung tingkat kepercayaan data berdasarkan kesamaan nama, prodi, dan institusi (Logika Tokenisasi).
- **Admin & Public Dashboard**: Panel manajemen untuk admin (Login protected) dan portal publik untuk pengunjung.
- **Manual Verification**: Fitur preview hasil pencarian bagi admin sebelum data disimpan ke database.
- **Cloud Persistence**: Terintegrasi penuh dengan Supabase sebagai database utama.

---

## 🏗️ Arsitektur Sistem
Sistem ini terdiri dari tiga komponen utama:
1. **Scraper Engine (`scraper_engine.py`)**: Bertanggung jawab menarik data mentah dari internet.
2. **Tracker Logic (`tracker.py`)**: Mesin pengolah yang melakukan tokenisasi dan perhitungan skor kecocokan.
3. **Streamlit App (`app.py`)**: Antarmuka pengguna berbasis web (UI/UX).

---

## 📋 Pengujian Kualitas (Daily Project 2)

Berikut adalah hasil pengujian aplikasi berdasarkan aspek kualitas yang telah ditentukan pada fase desain:

| Aspek Kualitas | Parameter Keberhasilan | Metode Pengujian | Status |
| :--- | :--- | :--- | :--- |
| **Akurasi (Accuracy)** | Skor > 80% menunjukkan kecocokan data yang valid antara input dan hasil internet. | Mencocokkan nama alumni UMM nyata dengan profil OpenAlex. | ✅ Passed |
| **Efisiensi (Efficiency)** | Proses pelacakan hingga penyimpanan data ke DB memakan waktu < 10 detik. | Pengukuran waktu eksekusi fungsi `scrape_alumni_data`. | ✅ Passed |
| **Auditabilitas** | Setiap data memiliki `evidence_url` yang dapat diverifikasi kebenarannya. | Pengecekan link bukti pada tabel alumni di dashboard. | ✅ Passed |
| **Integritas Data** | Tidak ada data duplikat untuk nama alumni yang sama di database. | Pengujian fitur `upsert` pada kolom `name` (Unique Constraint). | ✅ Passed |
| **Keamanan (Security)** | Fitur hapus dan tambah data hanya bisa diakses melalui login admin. | Percobaan akses fitur admin tanpa memasukkan password. | ✅ Passed |
| **Resiliensi** | Sistem tetap berjalan (Fallback) meskipun API utama tidak memberikan hasil. | Simulasi pencarian nama alumni yang tidak terdaftar di OpenAlex. | ✅ Passed |

---

## 🛠️ Cara Instalasi & Penggunaan

### 1. Prasyarat
- Python 3.9+
- Akun Supabase (URL dan API Key)

### 2. Instalasi Library
```bash
pip install streamlit pandas supabase python-dotenv thefuzz requests beautifulsoup4
