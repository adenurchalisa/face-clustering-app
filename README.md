# 📸 FaceCluster

Aplikasi web (Streamlit) untuk mendeteksi wajah pada kumpulan foto dan
mengelompokkan foto secara otomatis berdasarkan orang. Sumber foto bisa dari
upload langsung (gambar atau ZIP) atau folder Google Drive publik. Hasilnya
berupa cluster per-orang yang bisa diunduh sebagai ZIP.

## Persyaratan
- Python 3.10+
- (Opsional) `GOOGLE_API_KEY` — hanya untuk fitur download dari Google Drive

## Instalasi

> **Wajib** menggunakan virtual environment. Buat & aktifkan venv sebelum instalasi.

```bash
# 1. Buat virtual environment
python -m venv venv

# 2. Aktifkan venv
#    Windows (PowerShell):
venv\Scripts\Activate.ps1
#    Windows (Git Bash):
source venv/Scripts/activate
#    macOS / Linux:
source venv/bin/activate

# 3. Install dependency
pip install -r requirements.txt
```

Di Linux/Streamlit Cloud, dependency sistem ada di `packages.txt`
(`libgl1-mesa-glx`, `libglib2.0-0`).

## Menjalankan

```bash
streamlit run app.py
```

Buka http://localhost:8501 di browser.

## Konfigurasi Google Drive (opsional)
Untuk fitur download dari Google Drive, isi API key di
`.streamlit/secrets.toml` (file ini di-gitignore):

```toml
GOOGLE_API_KEY = "..."
```

Cara mendapatkan key: Google Cloud Console → buat project → enable
**Google Drive API** → Credentials → Create API Key.

## Cara pakai
1. **Upload** foto (atau ZIP) di tab Upload, atau tempel link folder Google
   Drive yang di-set *Anyone with the link*.
2. **Processing** — deteksi wajah (InsightFace) lalu clustering (UMAP + HDBSCAN).
3. **Hasil** — lihat cluster per orang dan unduh sebagai ZIP.

## Kontribusi
Gunakan **Conventional Commits**, buat commit yang **atomik** dan kecil agar
mudah dibaca, dan tulis pesan commit dalam **bahasa Inggris**.
