"""
Hyperparameter dari hasil eksperimen NB09 (UMAP + HDBSCAN).

Konfigurasi terbaik (NB09 - Best Coverage):
  Coverage Rate    : 99.3%
  Silhouette       : 0.9041
  n_clusters       : 95
  n_components     : 30
  n_neighbors      : 30
  min_cluster_size : 20
  min_samples      : 20
"""

import os

# Google Drive API
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# InsightFace
FACE_MODEL_NAME      = "buffalo_l"
FACE_DET_SIZE        = (640, 640)
FACE_DET_THRESHOLD   = 0.5
FACE_PADDING         = 0.1
FACE_MIN_CROP_SIZE   = 20
MAX_IMAGE_INPUT_SIZE = 1920  # Resize foto besar ke max dimensi ini sebelum deteksi (speedup)

# UMAP — konfigurasi terbaik dari NB09 (TETAP, tidak berubah antar dataset)
UMAP_N_COMPONENTS = 30
UMAP_N_NEIGHBORS  = 30
UMAP_MIN_DIST     = 0.0
UMAP_RANDOM_STATE = 42

# HDBSCAN — parameter dihitung adaptif di clustering.py
HDBSCAN_CLUSTER_SELECTION_METHOD = "eom"

# App limits
MAX_PHOTOS_UPLOAD = 3000
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".heic", ".heif"]
TEMP_DIR          = os.path.join(os.getenv("TMPDIR", os.getenv("TEMP", "/tmp")), "facecluster")

# UI
MAX_CLUSTER_PREVIEW   = 200   # batas absolut foto/cluster saat "tampilkan semua"
GALLERY_PREVIEW_INITIAL = 24  # foto yang ditampilkan awal per cluster (sebelum "tampilkan semua")
GALLERY_THUMB_MAX_DIM = 512   # downscale foto galeri sebelum di-embed base64 (jaga ukuran HTML)
GALLERY_JPEG_QUALITY  = 80    # kualitas JPEG untuk embed base64
MAX_NOISE_PREVIEW     = 12
