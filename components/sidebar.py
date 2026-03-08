import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.markdown("### 📸 FaceCluster")
        st.caption("Pengelompokan Foto Otomatis")
        st.markdown("---")

        # Navigasi
        pages = {
            "overview": "ℹ️ Overview",
            "upload": "📁 Upload",
            "processing": "⏳ Processing",
            "results": "📊 Hasil",
        }

        for key, label in pages.items():
            is_active = st.session_state.page == key
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = key
                st.rerun()

        # Status info
        st.markdown("---")
        photos = st.session_state.get("photos")
        clusters = st.session_state.get("clusters")
        face_stats = st.session_state.get("face_stats")

        if photos:
            st.success(f"📷 {len(photos)} foto loaded")
        if face_stats:
            st.info(f"👤 {face_stats['total_faces']} wajah terdeteksi")
        if clusters:
            st.success(f"👥 {len(clusters)} cluster terbentuk")