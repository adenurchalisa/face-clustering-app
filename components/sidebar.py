import streamlit as st


def render_sidebar():
    with st.sidebar:
        # ── Brand ──
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4F46E5, #7C3AED);
            border-radius: 14px;
            padding: 20px 16px;
            text-align: center;
            margin-bottom: 20px;
        ">
            <div style="font-size: 32px;">📸</div>
            <p style="color: white; font-weight: 800; font-size: 1.1rem; margin: 6px 0 2px 0;">FaceCluster</p>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.72rem; letter-spacing: 1.5px;
                      text-transform: uppercase; margin: 0;">Auto Photo Grouping</p>
        </div>
        """, unsafe_allow_html=True)

        # ── Navigasi ──
        pages = {
            "overview":   ("ℹ️",  "Overview"),
            "upload":     ("📁",  "Upload"),
            "processing": ("⏳",  "Processing"),
            "results":    ("📊",  "Hasil"),
        }

        current = st.session_state.page
        for key, (icon, label) in pages.items():
            is_active = current == key
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = key
                st.rerun()

        # ── Status ──
        photos     = st.session_state.get("photos")
        clusters   = st.session_state.get("clusters")
        face_stats = st.session_state.get("face_stats")

        if photos or clusters:
            st.markdown("---")
            st.markdown(
                "<p style='font-size:0.72rem; font-weight:700; text-transform:uppercase;"
                " letter-spacing:1px; color:#94A3B8; margin-bottom:8px;'>Status</p>",
                unsafe_allow_html=True,
            )
            if photos:
                st.markdown(f"""
                <div style="background:#EEF2FF; border-radius:10px; padding:10px 14px;
                            margin-bottom:6px;">
                    <span style="font-size:0.85rem; font-weight:600; color:#4F46E5;">
                        📷 {len(photos)} foto dimuat
                    </span>
                </div>
                """, unsafe_allow_html=True)
            if face_stats:
                st.markdown(f"""
                <div style="background:#F0FDF4; border-radius:10px; padding:10px 14px;
                            margin-bottom:6px;">
                    <span style="font-size:0.85rem; font-weight:600; color:#10B981;">
                        👤 {face_stats['total_faces']} wajah terdeteksi
                    </span>
                </div>
                """, unsafe_allow_html=True)
            if clusters:
                st.markdown(f"""
                <div style="background:#FDF4FF; border-radius:10px; padding:10px 14px;
                            margin-bottom:6px;">
                    <span style="font-size:0.85rem; font-weight:600; color:#7C3AED;">
                        👥 {len(clusters)} cluster terbentuk
                    </span>
                </div>
                """, unsafe_allow_html=True)
