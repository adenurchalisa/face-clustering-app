import logging
import os
import re
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from googleapiclient.discovery import build  # hanya untuk list files

from src.config import GOOGLE_API_KEY, TEMP_DIR, SUPPORTED_FORMATS, MAX_PHOTOS_UPLOAD

logger = logging.getLogger(__name__)
MAX_WORKERS = 20          # worker paralel
DOWNLOAD_TIMEOUT = 60     # detik timeout per file


def _get_api_key():
    """Ambil API key: prioritaskan st.secrets (Streamlit Cloud), lalu env var."""
    try:
        import streamlit as st
        key = st.secrets.get("GOOGLE_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return GOOGLE_API_KEY


def _build_service():
    api_key = _get_api_key()
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY belum dikonfigurasi. "
            "Tambahkan di .streamlit/secrets.toml (lokal) atau Streamlit Cloud secrets."
        )
    return build("drive", "v3", developerKey=api_key, cache_discovery=False)


def extract_drive_id(link):
    """Ekstrak folder/file ID dari Google Drive link."""
    folder_match = re.search(r'/folders/([a-zA-Z0-9_-]+)', link)
    if folder_match:
        return folder_match.group(1), "folder"

    file_match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', link)
    if file_match:
        return file_match.group(1), "file"

    id_match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', link)
    if id_match:
        return id_match.group(1), "file"

    return None, None


def _list_files_recursive(service, folder_id):
    """List semua file foto di folder secara rekursif, dengan pagination."""
    files = []
    page_token = None

    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
            pageSize=1000,
        ).execute()

        for item in response.get("files", []):
            if item["mimeType"] == "application/vnd.google-apps.folder":
                files.extend(_list_files_recursive(service, item["id"]))
            elif any(item["name"].lower().endswith(ext) for ext in SUPPORTED_FORMATS):
                files.append(item)

            if len(files) >= MAX_PHOTOS_UPLOAD:
                return files

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return files


def _download_file(api_key, file_id, dest_path):
    """Download satu file dari Drive menggunakan URL download langsung.
    Bekerja untuk file 'Anyone with the link' tanpa memerlukan OAuth.
    Menangani konfirmasi virus-scan Google untuk file besar (>25 MB).
    """
    session = requests.Session()
    url = f"https://drive.google.com/uc?export=download&id={file_id}"

    response = session.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT)
    response.raise_for_status()

    # Untuk file besar, Google Drive mengembalikan halaman HTML konfirmasi.
    # Deteksi dari Content-Type dan ekstrak token konfirmasi.
    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type:
        # Coba ekstrak confirm token (format lama: confirm=XXXX)
        confirm_match = re.search(r'confirm=([0-9A-Za-z_\-]+)', response.text)
        if confirm_match:
            confirm_token = confirm_match.group(1)
            url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm_token}"
        else:
            # Format baru: tombol "Download anyway" dengan UUID
            uuid_match = re.search(r'uuid=([0-9A-Za-z_\-]+)', response.text)
            if uuid_match:
                uuid = uuid_match.group(1)
                url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t&uuid={uuid}"
            else:
                # Fallback: tambahkan confirm=t saja
                url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
        response = session.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT)
        response.raise_for_status()

    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)


def _download_all_parallel(api_key, files, output_dir, progress_callback=None):
    """Download semua file secara paralel. Return: (list of path, first_error)."""
    photo_paths = []
    first_error = [None]
    lock = threading.Lock()
    completed = [0]

    def download_one(file_meta):
        dest_path = os.path.join(output_dir, file_meta["name"])
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(file_meta["name"])
            dest_path = os.path.join(output_dir, f"{base}_{file_meta['id'][:6]}{ext}")
        try:
            _download_file(api_key, file_meta["id"], dest_path)
            return dest_path, file_meta["name"]
        except Exception as e:
            logger.warning("Gagal unduh '%s': %s", file_meta["name"], e)
            # Simpan error pertama untuk ditampilkan ke user
            with lock:
                if first_error[0] is None:
                    first_error[0] = str(e)
            # Hapus file parsial
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass
            return None, file_meta["name"]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_one, f): f for f in files}
        for future in as_completed(futures):
            dest_path, filename = future.result()
            with lock:
                completed[0] += 1
                if dest_path:
                    photo_paths.append(dest_path)
                if progress_callback:
                    progress_callback(completed[0], len(files), filename)

    return photo_paths, first_error[0]


def download_from_drive(link, output_dir=None, progress_callback=None):
    """
    Download foto dari Google Drive menggunakan Google Drive API v3.
    - progress_callback(current, total, filename) dipanggil setiap file selesai diunduh.
    Return: (photo_paths, error_message)
    """
    if output_dir is None:
        output_dir = os.path.join(TEMP_DIR, "drive_photos")

    # Bersihkan sisa sesi sebelumnya
    # ignore_errors=True: Windows mengunci file yang sedang dipakai proses lain,
    # file lama yang terkunci dibiarkan — tidak mempengaruhi hasil karena
    # photo_paths hanya berisi file yang baru diunduh
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)

    drive_id, link_type = extract_drive_id(link)
    if drive_id is None:
        return [], "Link Google Drive tidak valid. Pastikan formatnya benar."

    try:
        service = _build_service()
    except ValueError as e:
        return [], str(e)

    try:
        if link_type == "folder":
            files = _list_files_recursive(service, drive_id)
        else:
            meta = service.files().get(fileId=drive_id, fields="id, name, mimeType").execute()
            if any(meta["name"].lower().endswith(ext) for ext in SUPPORTED_FORMATS):
                files = [meta]
            else:
                files = []
    except Exception as e:
        return [], f"Gagal membaca isi Google Drive: {str(e)}"

    if not files:
        return [], "Tidak ada foto valid ditemukan. Pastikan folder berisi file JPG/PNG/HEIC."

    files = files[:MAX_PHOTOS_UPLOAD]
    api_key = _get_api_key()

    photo_paths, download_error = _download_all_parallel(api_key, files, output_dir, progress_callback)

    if not photo_paths:
        detail = f" Detail: {download_error}" if download_error else ""
        return [], f"Semua file gagal diunduh. Pastikan folder di-set 'Anyone with the link'.{detail}"

    return photo_paths, None
