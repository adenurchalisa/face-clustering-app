import streamlit as st
from src.pipeline import run_full_pipeline
from components import reset_session_state


def render():
    photos = st.session_state.get("photos")

    if not photos:
        st.warning("Tidak ada foto untuk diproses.")
        if st.button("← Kembali ke Upload"):
            st.session_state.page = "upload"
            st.rerun()
        return

    # ── Sudah diproses sebelumnya ──
    if st.session_state.get("clusters"):
        st.markdown("""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:14px;
                    padding:24px; text-align:center; margin-bottom:16px;">
            <div style="font-size:40px; margin-bottom:8px;">✅</div>
            <p style="font-weight:700; color:#065F46; font-size:1rem; margin:0;">
                Foto sudah diproses sebelumnya
            </p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Lihat Hasil", type="primary", use_container_width=True):
                st.session_state.page = "results"
                st.rerun()
        with col2:
            if st.button("🔄 Proses Ulang", use_container_width=True):
                reset_session_state()
                st.rerun()
        return

    # ── Header ──
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #EEF2FF, #F5F3FF);
                border-radius: 16px; padding: 28px 32px; margin-bottom: 20px;
                border: 1px solid #C7D2FE;">
        <h2 style="margin:0 0 6px 0; color:#3730A3; font-weight:800;">⏳ Memproses Foto</h2>
        <p style="margin:0; color:#6366F1; font-size:0.95rem;">
            Mendeteksi wajah dan mengelompokkan dari <b>{len(photos)}</b> foto —
            proses ini bisa memakan beberapa menit
        </p>
    </div>
    """, unsafe_allow_html=True)

    progress_placeholder = st.empty()
    success = run_full_pipeline(photos, progress_placeholder)

    if success:
        metrics    = st.session_state.get("metrics", {})
        face_stats = st.session_state.get("face_stats", {})

        st.balloons()

        st.markdown("""
        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:14px;
                    padding:20px; text-align:center; margin:16px 0;">
            <div style="font-size:36px;">🎉</div>
            <p style="font-weight:700; color:#065F46; font-size:1.05rem; margin:8px 0 0 0;">
                Pengelompokan selesai!
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4, gap="medium")
        col1.metric("📷 Total Foto",       face_stats.get("total_photos", 0))
        col2.metric("👤 Wajah Terdeteksi", face_stats.get("total_faces", 0))
        col3.metric("👥 Cluster",          metrics.get("n_clusters", 0))
        col4.metric("✅ Coverage",         f"{metrics.get('coverage_pct', 0)}%")

        st.markdown("<br>", unsafe_allow_html=True)
        _, col_btn, _ = st.columns([1, 2, 1])
        with col_btn:
            if st.button("📊  Lihat Hasil", type="primary", use_container_width=True):
                st.session_state.page = "results"
                st.rerun()
    else:
        st.markdown("""
        <div style="background:#FFF1F2; border:1px solid #FECDD3; border-radius:14px;
                    padding:20px; text-align:center; margin:16px 0;">
            <div style="font-size:36px;">❌</div>
            <p style="font-weight:700; color:#9F1239; font-size:1rem; margin:8px 0 4px 0;">
                Proses gagal — Tidak ada wajah terdeteksi
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Diagnostik: tampilkan face_stats untuk membantu debug
        face_stats = st.session_state.get("face_stats", {})
        if face_stats:
            st.markdown("**Info diagnostik:**")
            col1, col2, col3 = st.columns(3)
            col1.metric("📷 Foto diproses", face_stats.get("total_photos", 0))
            col2.metric("⚠️ Foto error/skip", face_stats.get("skipped_errors", 0))
            col3.metric("🔍 Foto tanpa wajah", face_stats.get("photos_without_faces", 0))

            skipped = face_stats.get("skipped_errors", 0)
            total   = face_stats.get("total_photos", 0)
            if skipped == total:
                st.error("Semua foto gagal dibaca (error saat loading). "
                         "Kemungkinan format file tidak didukung atau file korup.")
            elif skipped > 0:
                st.warning(f"{skipped} foto gagal dibaca. "
                           "Sisanya terbaca tapi tidak ada wajah yang terdeteksi.")
            else:
                st.info("Semua foto berhasil dibaca, tapi InsightFace tidak menemukan wajah. "
                        "Kemungkinan: foto terlalu kecil, wajah terlalu jauh, "
                        "atau foto bukan foto orang.")

        _, col_btn2, _ = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("← Coba Lagi", use_container_width=True):
                st.session_state.page = "upload"
                st.rerun()
