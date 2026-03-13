"""
Semua hyperparameter dan konstanta.
Nilai-nilai ini berasal dari hasil eksperimen NB05 (FAISS + HDBSCAN).

Konfigurasi terbaik (Final NB05):
  Coverage Rate : 92.36%
  Silhouette    : 0.3673
  n_clusters    : 144
"""

import os

# Google Drive API
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# InsightFace
FACE_MODEL_NAME    = "buffalo_l"    # Model InsightFace untuk deteksi + embedding
FACE_DET_SIZE      = (640, 640)     # Ukuran input face detection
FACE_DET_THRESHOLD = 0.5            # Confidence threshold deteksi wajah
FACE_PADDING       = 0.1            # Padding crop wajah (10% dari bounding box)
FACE_MIN_CROP_SIZE = 20             # Ukuran minimum crop wajah dalam pixel

# HDBSCAN — dari hasil eksperimen NB05 (Final)
# Langsung ke embedding 512-dim (L2-normalized), tanpa UMAP
HDBSCAN_MIN_CLUSTER_SIZE         = 50           # Minimum anggota per cluster
HDBSCAN_MIN_SAMPLES              = 5            # Kontrol konservatisme noise
HDBSCAN_CLUSTER_SELECTION_METHOD = "eom"        # "eom" atau "leaf"
HDBSCAN_METRIC                   = "euclidean"  # equiv. cosine karena embedding sudah L2-normalized

# App limits
MAX_PHOTOS_UPLOAD = 3000
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".heic", ".heif"]
TEMP_DIR          = "/tmp/facecluster"

# UI
MAX_CLUSTER_PREVIEW = 18
MAX_NOISE_PREVIEW   = 12
