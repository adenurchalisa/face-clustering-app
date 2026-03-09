import streamlit as st
from src.pipeline import run_full_pipeline
from components import reset_session_state


def render():
    st.header("⏳ Memproses Foto")

    photos = st.session_state.get("photos")

    if not photos:
        st.warning("Tidak ada foto untuk diproses.")
        if st.button("← Kembali ke Upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    # Cek apakah sudah pernah diproses (ada hasil)
    if st.session_state.get("clusters"):
        st.success("Foto sudah diproses sebelumnya!")
        if st.button("📊 Lihat Hasil", type="primary", use_container_width=True):
            st.session_state.page = "results"
            st.rerun()
        if st.button("🔄 Proses Ulang"):
            reset_session_state()
            st.rerun()
        return

    # Jalankan pipeline
    st.info(f"Memproses {len(photos)} foto... Ini bisa memakan waktu beberapa menit.")
    progress_placeholder = st.empty()

    success = run_full_pipeline(photos, progress_placeholder)

    if success:
        metrics = st.session_state.get("metrics", {})
        face_stats = st.session_state.get("face_stats", {})

        st.balloons()
        st.success("Pengelompokan selesai!")

        # Ringkasan
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Foto", face_stats.get("total_photos", 0))
        col2.metric("Wajah Terdeteksi", face_stats.get("total_faces", 0))
        col3.metric("Cluster", metrics.get("n_clusters", 0))
        col4.metric("Coverage", f"{metrics.get('coverage_pct', 0)}%")

        if st.button("📊 Lihat Hasil", type="primary", use_container_width=True):
            st.session_state.page = "results"
            st.rerun()
    else:
        st.error("Proses gagal. Pastikan foto mengandung wajah yang jelas.")
        if st.button("← Coba Lagi"):
            st.session_state.page = "upload"
            st.rerun()