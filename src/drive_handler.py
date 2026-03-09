import os
import re
import subprocess
from src.config import TEMP_DIR, SUPPORTED_FORMATS, MAX_PHOTOS_UPLOAD


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


def download_from_drive(link, output_dir=None):
    """
    Download foto dari Google Drive link menggunakan gdown CLI.
    Return: (photo_paths, error_message)
    """
    if output_dir is None:
        output_dir = os.path.join(TEMP_DIR, "drive_photos")

    os.makedirs(output_dir, exist_ok=True)

    drive_id, link_type = extract_drive_id(link)
    if drive_id is None:
        return [], "Link Google Drive tidak valid. Pastikan formatnya benar."

    try:
        if link_type == "folder":
            # Gunakan gdown CLI dengan flag --folder dan --remaining-ok
            # --remaining-ok: lanjutkan meskipun ada file yang gagal
            url = f"https://drive.google.com/drive/folders/{drive_id}"
            result = subprocess.run(
                ["gdown", "--folder", "--remaining-ok", "-O", output_dir, url],
                capture_output=True,
                text=True,
                timeout=600,  # 10 menit timeout
            )
            if result.returncode != 0 and not os.listdir(output_dir):
                return [], f"Gagal download: {result.stderr[:200]}"
        else:
            import gdown
            url = f"https://drive.google.com/uc?id={drive_id}"
            gdown.download(url, output=output_dir, quiet=True)
    except subprocess.TimeoutExpired:
        return [], "Download timeout. Coba upload ZIP langsung sebagai alternatif."
    except Exception as e:
        return [], f"Gagal download dari Google Drive: {str(e)}"

    # Kumpulkan foto valid
    photo_paths = []
    reached_limit = False
    for root, dirs, files in os.walk(output_dir):
        if reached_limit:
            break
        for f in sorted(files):
            if len(photo_paths) >= MAX_PHOTOS_UPLOAD:
                reached_limit = True
                break
            if any(f.lower().endswith(ext) for ext in SUPPORTED_FORMATS):
                photo_paths.append(os.path.join(root, f))

    if not photo_paths:
        return [], "Tidak ada foto valid ditemukan. Pastikan folder berisi file JPG/PNG."

    return photo_paths, None