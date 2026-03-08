import os
import io
import zipfile
import shutil
from PIL import Image
import numpy as np
from src.config import TEMP_DIR, SUPPORTED_FORMATS, MAX_PHOTOS_UPLOAD

HEIC_FORMATS = (".heic", ".heif")


def save_uploaded_files(uploaded_files):
    """Simpan file upload user ke direktori temporer. Return: list of photo paths."""
    output_dir = os.path.join(TEMP_DIR, "uploads")
    os.makedirs(output_dir, exist_ok=True)

    photo_paths = []

    for f in uploaded_files:
        if len(photo_paths) >= MAX_PHOTOS_UPLOAD:
            break

        name_lower = f.name.lower()

        # Handle ZIP
        if name_lower.endswith(".zip"):
            zip_bytes = io.BytesIO(f.getbuffer())
            with zipfile.ZipFile(zip_bytes, "r") as zf:
                for entry in zf.namelist():
                    if len(photo_paths) >= MAX_PHOTOS_UPLOAD:
                        break

                    if not any(entry.lower().endswith(ext) for ext in SUPPORTED_FORMATS):
                        continue

                    # Guard: Zip Slip protection
                    safe_path = os.path.realpath(os.path.join(output_dir, entry))
                    if not safe_path.startswith(os.path.realpath(output_dir)):
                        continue

                    extracted = zf.extract(entry, output_dir)
                    photo_paths.append(extracted)

        # Handle HEIC/HEIF
        elif name_lower.endswith(HEIC_FORMATS):
            path = os.path.join(output_dir, f.name)
            with open(path, "wb") as out:
                out.write(f.getbuffer())

            converted = convert_heic_to_jpg(path)
            if converted:
                photo_paths.append(converted)

        # Handle foto biasa
        elif any(name_lower.endswith(ext) for ext in SUPPORTED_FORMATS):
            path = os.path.join(output_dir, f.name)
            with open(path, "wb") as out:
                out.write(f.getbuffer())
            photo_paths.append(path)

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
    except Exception:
        return None


def create_cluster_zip(clusters, selected_ids):
    """
    Buat ZIP dari cluster yang dipilih.
    Struktur: Cluster_1/foto1.jpg, Cluster_2/foto2.jpg, ...
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for cid in selected_ids:
            if cid not in clusters:
                continue

            folder_name = f"Cluster_{cid + 1}"
            added_photos = set()

            for face in clusters[cid]:
                photo_path = face["source_photo"]
                if photo_path in added_photos:
                    continue
                added_photos.add(photo_path)

                filename = os.path.basename(photo_path)
                arcname = f"{folder_name}/{filename}"
                zf.write(photo_path, arcname)

    zip_buffer.seek(0)
    return zip_buffer


def numpy_to_pil(img_array):
    """Convert numpy array RGB ke PIL Image."""
    return Image.fromarray(img_array.astype(np.uint8))


def cleanup_temp():
    """Hapus semua file temporer."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)