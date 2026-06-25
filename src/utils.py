import logging
import os
import io
import zipfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
from PIL import Image
import numpy as np
from src.config import TEMP_DIR, SUPPORTED_FORMATS, MAX_PHOTOS_UPLOAD

logger = logging.getLogger(__name__)

HEIC_FORMATS = (".heic", ".heif")
UPLOAD_MAX_WORKERS = 8


def _write_regular_file(f, output_dir):
    """Tulis satu file upload (biasa atau HEIC) ke disk. Return: path foto, atau None."""
    path = os.path.join(output_dir, f.name)
    with open(path, "wb") as out:
        out.write(f.getbuffer())

    if f.name.lower().endswith(HEIC_FORMATS):
        return convert_heic_to_jpg(path)
    return path


def _extract_zip_entry(zip_bytes, entry, output_dir):
    """Ekstrak satu entry ZIP ke disk. Return: path foto, atau None."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
        # Guard: Zip Slip protection
        safe_path = os.path.realpath(os.path.join(output_dir, entry))
        if not safe_path.startswith(os.path.realpath(output_dir)):
            return None

        extracted = zf.extract(entry, output_dir)

    if entry.lower().endswith(HEIC_FORMATS):
        return convert_heic_to_jpg(extracted)
    return extracted


def save_uploaded_files(uploaded_files):
    """Simpan file upload user ke direktori temporer (paralel). Return: list of photo paths."""
    output_dir = os.path.join(TEMP_DIR, "uploads")
    os.makedirs(output_dir, exist_ok=True)

    tasks = []
    n_planned = 0

    for f in uploaded_files:
        if n_planned >= MAX_PHOTOS_UPLOAD:
            break

        name_lower = f.name.lower()

        if name_lower.endswith(".zip"):
            zip_bytes = bytes(f.getbuffer())
            with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
                for entry in zf.namelist():
                    if n_planned >= MAX_PHOTOS_UPLOAD:
                        break
                    if not any(entry.lower().endswith(ext) for ext in SUPPORTED_FORMATS):
                        continue
                    tasks.append((_extract_zip_entry, (zip_bytes, entry, output_dir)))
                    n_planned += 1

        elif any(name_lower.endswith(ext) for ext in SUPPORTED_FORMATS):
            tasks.append((_write_regular_file, (f, output_dir)))
            n_planned += 1

    photo_paths = []
    with ThreadPoolExecutor(max_workers=UPLOAD_MAX_WORKERS) as executor:
        futures = [executor.submit(fn, *args) for fn, args in tasks]
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    photo_paths.append(result)
            except Exception as e:
                logger.warning("Gagal menyimpan file upload: %s", e)

    return photo_paths


def convert_heic_to_jpg(heic_path):
    """Konversi file HEIC/HEIF ke JPG. Return: path JPG baru, atau None jika gagal."""
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()

        img = Image.open(heic_path)
        jpg_path = os.path.splitext(heic_path)[0] + ".jpg"
        img.convert("RGB").save(jpg_path, "JPEG", quality=95)

        os.remove(heic_path)
        return jpg_path
    except Exception as e:
        logger.warning("Gagal konversi HEIC '%s': %s", heic_path, e)
        return None


def _cluster_signature(clusters, selected_ids):
    """Signature ringan & hashable dari cluster terpilih, dipakai sebagai cache key
    (hindari hash langsung atas numpy array crop/embedding yang besar)."""
    return tuple(
        (cid, tuple((f["source_photo"], round(f["det_score"], 4)) for f in clusters.get(cid, [])))
        for cid in selected_ids
    )


@st.cache_data(show_spinner=False)
def _build_cluster_zip(_clusters, selected_ids, signature):
    """
    Buat ZIP dari cluster yang dipilih.
    Struktur: Cluster_1/foto1.jpg, Cluster_2/foto2.jpg, ...
    `signature` (lihat _cluster_signature) jadi cache key; `_clusters` diawali underscore
    agar Streamlit tidak mencoba hash isinya secara langsung.
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for cid in selected_ids:
            if cid not in _clusters:
                continue

            folder_name = f"Cluster_{cid + 1}"
            faces = _clusters[cid]

            if not faces:
                continue

            # Tambah _preview.jpg — wajah representatif (skor deteksi tertinggi)
            rep_face = max(faces, key=lambda f: f["det_score"])
            preview_buf = io.BytesIO()
            numpy_to_pil(rep_face["crop"]).save(preview_buf, "JPEG", quality=90)
            zf.writestr(f"{folder_name}/_preview.jpg", preview_buf.getvalue())

            # Tambah foto asli (unik)
            added_photos = set()
            for face in faces:
                photo_path = face["source_photo"]
                if photo_path in added_photos:
                    continue
                added_photos.add(photo_path)

                filename = os.path.basename(photo_path)
                arcname = f"{folder_name}/{filename}"
                zf.write(photo_path, arcname)

    zip_buffer.seek(0)
    return zip_buffer


def create_cluster_zip(clusters, selected_ids):
    """Wrapper publik — bangun signature ringan lalu delegasikan ke versi cached."""
    selected_ids = tuple(selected_ids)
    signature = _cluster_signature(clusters, selected_ids)
    return _build_cluster_zip(clusters, selected_ids, signature)


def numpy_to_pil(img_array):
    """Convert numpy array RGB ke PIL Image."""
    return Image.fromarray(img_array.astype(np.uint8))


def cleanup_temp():
    """Hapus semua file temporer."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)