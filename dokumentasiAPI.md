# Dokumentasi API Backend (Google Apps Script)

Script Python `email_broadcaster.py` ini adalah *client* yang mengharapkan *backend* API (dibuat dengan Google Apps Script) yang mematuhi spesifikasi berikut.

## 1. Endpoint: Health Check

Untuk memverifikasi API aktif dan terhubung.

* **Method:** `GET`
* **URL:** `https://script.google.com/.../exec?path=health`
* **Respon Sukses (JSON):**
    ```json
    {
      "success": true,
      "data": {
        "status": "healthy",
        "version": "1.0",
        "services": "gmail"
      }
    }
    ```

## 2. Endpoint: Kirim Email

Untuk mengirim satu email. Script Python akan me-looping dan memanggil endpoint ini berulang kali.

* **Method:** `POST`
* **URL:** `https://script.google.com/.../exec`
* **Headers:**
    * `Content-Type: application/json`
* **Request Body (JSON):**
    ```json
    {
      "endpoint": "send-email",
      "api_key": "API_KEY_ANDA",
      "to": "penerima@email.com",
      "subject": "Ini adalah subject",
      "body": "Ini adalah isi email plain text.",
      "from_name": "Nama Pengirim",
      "html_body": "<h1>Opsional:</h1><p>Isi email dalam HTML.</p>",
      "cc": "cc@email.com",
      "bcc": "bcc@email.com"
    }
    ```
    *Catatan: `html_body`, `cc`, dan `bcc` bersifat opsional.*

* **Respon Sukses (JSON):**
    Script ini mengharapkan respon JSON dengan `success: true` dan idealnya menyertakan `messageId`.
    ```json
    {
      "success": true,
      "data": {
        "messageId": "gas-message-id-12345"
      }
    }
    ```

* **Respon Gagal (JSON):**
    Jika gagal, kirimkan `success: false` beserta pesan error.
    ```json
    {
      "success": false,
      "error": {
        "message": "API Key tidak valid."
      }
    }
    ```
