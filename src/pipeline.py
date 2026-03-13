import logging
import streamlit as st
from src.face_extractor import process_all_photos
from src.clustering import run_clustering_pipeline

logger = logging.getLogger(__name__)


def run_full_pipeline(photo_paths, progress_placeholder):
    """
    Jalankan pipeline lengkap dan update progress di UI.
    Simpan hasil ke st.session_state.
    """
    progress_bar = progress_placeholder.progress(0, text="Memulai...")

    try:
        # STEP 1: Face Detection & Embedding (0-50%)
        def face_progress(current, total, msg):
            pct = int((current / total) * 50)
            progress_bar.progress(pct, text=msg)

        all_faces, face_stats = process_all_photos(photo_paths, face_progress)
        st.session_state.face_stats = face_stats

        if not all_faces:
            progress_bar.progress(100, text="Tidak ada wajah terdeteksi!")
            return False

        # STEP 2: HDBSCAN Clustering (50-100%)
        def cluster_progress(current, total, msg):
            pct = 50 + int((current / total) * 50)
            progress_bar.progress(pct, text=msg)

        clusters, noise_faces, metrics = run_clustering_pipeline(all_faces, cluster_progress)

        # Simpan ke session state
        st.session_state.clusters = clusters
        st.session_state.noise_faces = noise_faces
        st.session_state.metrics = metrics

        progress_bar.progress(100, text="Selesai!")
        return True

    except Exception as e:
        logger.error("Pipeline gagal: %s", e, exc_info=True)
        progress_bar.progress(100, text=f"Error: {str(e)}")
        st.error(f"Pipeline gagal: {e}")
        return False