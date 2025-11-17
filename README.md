# py-gas-broadcaster 🚀

Script Python CLI sederhana namun *powerful* untuk mengirim broadcast email yang dipersonalisasi. Script ini bertindak sebagai **client** yang terhubung ke **Google Apps Script (GAS) API** Anda sendiri.

Solusi ini sempurna jika Anda perlu mengirim ratusan email dari daftar CSV atau Excel tanpa harus berlangganan layanan email marketing yang mahal.

## 🎯 Fitur Utama

* **Broadcast dari Data Lokal:** Baca daftar penerima (nama, email) langsung dari file `.csv` atau `.xlsx`.
* **Validasi Data:** Otomatis mengecek format email yang valid dan menghapus data yang kosong.
* **Personalisasi:** Gunakan `{nama}` di dalam *subject* dan *body* email untuk sentuhan personal.
* **Support HTML & Plain Text:** Kirim email HTML yang cantik atau email *plain text* yang ringan.
* **Anti-Rate Limit:** Terdapat *delay* dan *batching* yang bisa diatur agar tidak di-banned oleh Google.
* **Cek Kesehatan API:** Memiliki fungsi `check_api_health()` untuk memastikan API Anda berjalan sebelum mengirim.
* **Logging Hasil:** Simpan laporan pengiriman (berhasil/gagal) ke dalam file `.csv`.

## ⚙️ Cara Kerjanya?

Repo ini **HANYA** berisi script Python (Client). Anda **WAJIB** membuat backend API sendiri menggunakan Google Apps Script yang di-*deploy* sebagai Web App.

1.  **Backend (Google Apps Script):** Anda membuat script di Google (misal: `GmailApp.sendEmail()`) dan men-deploy-nya.
2.  **Frontend (Script Python Ini):** Script ini akan membaca file Excel Anda, lalu mengirim permintaan `POST` ke API GAS Anda satu per satu untuk setiap penerima.

Lihat `dokumentasiAPI.md` untuk spesifikasi API yang diharapkan oleh script ini.

## 🚀 Persiapan

1.  **Python & Libraries:**
    Pastikan Anda memiliki Python 3.x.
    ```bash
    pip install pandas requests
    ```

2.  **Buat API Google Apps Script Anda:**
    * Buat project baru di [script.google.com](https://script.google.com/).
    * Salin kode dari [contoh API backend](link-ke-file-gas-anda-jika-ada) atau buat sendiri sesuai `dokumentasiAPI.md`.
    * Deploy sebagai **Web App**.
    * **PENTING:** Atur agar Web App bisa diakses oleh "Anyone" (jika menggunakan API Key) atau "Anyone, even anonymous" jika Anda tidak ingin repot dengan otentikasi Google.
    * Salin **URL Web App** Anda.

## 🔧 Konfigurasi Script

Buka file `main.py` dan ubah dua variabel ini di dalam fungsi `main()`:

```python
def main():
    # Ganti dengan URL deployment Google Apps Script Anda
    API_URL = "[https://script.google.com/macros/s/URL_API_ANDA/exec](https://script.google.com/macros/s/URL_API_ANDA/exec)"
    
    # Ganti dengan API Key yang Anda set di dalam script GAS
    API_KEY = "SECRET_KEY_ANDA"
    
    # ... sisanya ...
```

## ▶️ Cara Penggunaan

Jalankan script dari terminal Anda:

```bash
python3 email_broadcaster.py
```

Script ini akan memandu Anda secara interaktif:

1.  Mengecek status API.
2.  Meminta tipe file (CSV/Excel).
3.  Meminta *path* file.
4.  Menampilkan 5 data pertama dan meminta konfirmasi.
5.  Meminta Nama Pengirim, Subject, dan Isi Email (mendukung input *multi-line*).
6.  Memulai proses broadcast.
7.  Menyimpan hasil jika diperlukan.

## 📝 Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT.
