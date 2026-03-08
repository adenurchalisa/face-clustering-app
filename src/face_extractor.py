import numpy as np
import cv2
import streamlit as st
from insightface.app import FaceAnalysis
from src.config import FACE_MODEL_NAME, FACE_DET_SIZE, FACE_DET_THRESHOLD

@st.cache_resource
def load_model():
    import onnxruntime as ort
    
    available = ort.get_available_providers()
    if "CUDAExecutionProvider" in available:
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    else:        
        providers = ["CPUExecutionProvider"]
    
    app = FaceAnalysis(name=FACE_MODEL_NAME, providers=providers)
    app.prepare(ctx_id=0, det_size=FACE_DET_SIZE, det_thresh=FACE_DET_THRESHOLD)
    return app

def extract_faces(image_path, model=None):
    
    if model is None:
        model = load_model()

    img = cv2.imread(image_path)
    if img is None:
        return []

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = model.get(img_rgb)

    results = []
    for face in faces:
        if face.det_score < FACE_DET_THRESHOLD:
            continue
        if face.embedding is None:
            continue

        # Crop wajah dengan sedikit padding
        bbox = face.bbox.astype(int)
        x1, y1, x2, y2 = bbox
        h, w = img_rgb.shape[:2]
        pad = int(max(x2 - x1, y2 - y1) * 0.1)
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(w, x2 + pad)
        y2 = min(h, y2 + pad)
        crop = img_rgb[y1:y2, x1:x2]
        
        if crop.size == 0 or (x2 - x1) < 20 or (y2 - y1) < 20:
            continue

        results.append({
            "bbox": bbox.tolist(),
            "embedding": face.embedding,
            "crop": crop,
            "det_score": float(face.det_score),
            "source_photo": image_path,
        })

    return results

def process_all_photos(photo_paths, progress_callback=None):
    model = load_model()
    all_faces = []
    photos_with_faces = 0
    skipped = 0
    
    for i, path in enumerate(photo_paths):
        if progress_callback:
            progress_callback(i+1, len(photo_paths), f"Mendeteksi wajah : {i+1}/{len(photo_paths)}")
        try:
            faces = extract_faces(path, model=model)
            if faces:
                photos_with_faces += 1
            all_faces.extend(faces)
        except Exception as e :
            skipped += 1
            continue
    
    stats = {
        "total_photos": len(photo_paths),
        "photos_with_faces": photos_with_faces,
        "photos_without_faces": len(photo_paths) - photos_with_faces - skipped,
        "skipped_errors": skipped,
        "total_faces": len(all_faces),
    }
        
    return all_faces, stats