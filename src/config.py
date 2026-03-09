import os
import tempfile

# InsightFace
FACE_MODEL_NAME = "buffalo_l"
FACE_DET_SIZE = (640, 640)
FACE_DET_THRESHOLD = 0.5

# --- UMAP (dari NB9) ---
UMAP_N_COMPONENTS = 30
UMAP_N_NEIGHBORS = 30
UMAP_MIN_DIST = 0.0
UMAP_METRIC = "cosine"
UMAP_RANDOM_STATE = 42

# --- HDBSCAN (dari NB9) ---
HDBSCAN_MIN_CLUSTER_SIZE = 20
HDBSCAN_MIN_SAMPLES = 20
HDBSCAN_CLUSTER_SELECTION_METHOD = "eom"

# --- Batas Aplikasi ---
MAX_PHOTOS_UPLOAD = 5000
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".heic", ".heif"]
TEMP_DIR = os.path.join(tempfile.gettempdir(), "facecluster")

# --- Konstanta UI & Deteksi ---
FACE_PADDING = 0.1          # Padding wajah saat crop (10% dari ukuran bounding box)
FACE_MIN_CROP_SIZE = 20     # Ukuran minimum crop wajah dalam pixel
MAX_CLUSTER_PREVIEW = 18    # Maksimum wajah yang ditampilkan per cluster di gallery
MAX_NOISE_PREVIEW = 12      # Maksimum wajah noise yang ditampilkan