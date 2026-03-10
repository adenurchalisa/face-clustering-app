import streamlit as st


def render():
    # ── Hero Section ──
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        border-radius: 20px;
        padding: 56px 40px;
        text-align: center;
        margin-bottom: 8px;
        box-shadow: 0 8px 32px rgba(79, 70, 229, 0.25);
    ">
        <div style="font-size: 56px; margin-bottom: 12px;">📸</div>
        <h1 style="
            color: white !important;
            font-size: 2.8rem;
            font-weight: 800;
            margin: 0 0 12px 0;
            letter-spacing: -1px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.15);
        ">FaceCluster</h1>
        <p style="
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
            font-weight: 500;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin: 0 0 16px 0;
        ">AUTO PHOTO GROUPING SYSTEM</p>
        <p style="
            color: rgba(255,255,255,0.8);
            font-size: 1rem;
            max-width: 560px;
            margin: 0 auto;
            line-height: 1.6;
        ">Pengelompokan foto otomatis berdasarkan identitas wajah menggunakan AI.
        Upload foto dokumentasi, sistem mendeteksi & mengelompokkan setiap wajah secara otomatis.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Steps ──
    st.markdown("### Cara Menggunakan")

    steps = [
        ("#EEF2FF", "#4F46E5", "📁", "1. Upload Foto",
         "Upload file foto, ZIP, atau tempel link Google Drive"),
        ("#F0FDF4", "#10B981", "🔍", "2. Deteksi Wajah",
         "AI mendeteksi setiap wajah dan mengekstraksi fitur uniknya"),
        ("#FFF7ED", "#F59E0B", "🧩", "3. Pengelompokan",
         "Wajah yang sama dikelompokkan — 1 cluster = 1 orang"),
        ("#FDF2F8", "#EC4899", "📥", "4. Download",
         "Pilih cluster & download foto per orang sebagai ZIP"),
    ]

    cols = st.columns(4, gap="medium")
    for col, (bg, accent, icon, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div style="
                background: {bg};
                border-radius: 16px;
                padding: 24px 20px;
                text-align: center;
                height: 100%;
                border: 1px solid {accent}22;
                transition: box-shadow 0.2s;
            ">
                <div style="font-size: 36px; margin-bottom: 12px;">{icon}</div>
                <p style="font-weight: 700; color: {accent}; font-size: 0.95rem; margin: 0 0 8px 0;">{title}</p>
                <p style="color: #64748B; font-size: 0.82rem; line-height: 1.5; margin: 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tech Stack ──
    st.markdown("### Teknologi yang Digunakan")

    techs = [
        ("🧠", "InsightFace", "Face Detection & Recognition Embedding", "#4F46E5"),
        ("📐", "UMAP", "Dimensionality Reduction", "#7C3AED"),
        ("🔵", "HDBSCAN", "Density-based Clustering", "#06B6D4"),
        ("⚡", "Streamlit", "Interactive Web Interface", "#EC4899"),
    ]

    cols2 = st.columns(4, gap="medium")
    for col, (icon, name, desc, color) in zip(cols2, techs):
        with col:
            st.markdown(f"""
            <div style="
                background: white;
                border: 1px solid #E8EAFF;
                border-radius: 14px;
                padding: 20px 16px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(79,70,229,0.06);
            ">
                <div style="font-size: 28px; margin-bottom: 8px;">{icon}</div>
                <p style="font-weight: 700; color: {color}; font-size: 0.9rem; margin: 0 0 4px 0;">{name}</p>
                <p style="color: #94A3B8; font-size: 0.75rem; margin: 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── CTA ──
    _, col_c, _ = st.columns([1, 2, 1])
    with col_c:
        if st.button("🚀  Mulai Pengelompokan", type="primary", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#94A3B8; font-size:0.78rem;'>"
        "Skripsi — Ade Nurchalisa · 60200122039 · UIN Alauddin Makassar · 2026"
        "</p>",
        unsafe_allow_html=True,
    )
