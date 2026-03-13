import os
import tempfile

# InsightFace
FACE_MODEL_NAME = "buffalo_l"
FACE_DET_SIZE = (640, 640)
FACE_DET_THRESHOLD = 0.5

# --- HDBSCAN ---
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
MAX_IMAGE_INPUT_SIZE = 1920 # Resize foto besar ke max dimensi ini sebelum deteksi (speedup)
MAX_CLUSTER_PREVIEW = 12    # Maksimum foto penuh yang ditampilkan per cluster di gallery
MAX_NOISE_PREVIEW = 12      # Maksimum wajah noise yang ditampilkan