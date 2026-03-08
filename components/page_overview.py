import streamlit as st


def render():
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<h1 style='text-align:center; margin-bottom:0'>📸 FaceCluster</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align:center; color:#F59E0B; font-weight:600; letter-spacing:2px'>"
            "AUTO PHOTO GROUPING SYSTEM</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "Sistem pengelompokan foto otomatis berdasarkan identitas wajah menggunakan AI. "
        "Upload koleksi foto dokumentasi, biarkan sistem mendeteksi dan mengelompokkan "
        "setiap wajah, lalu download hasilnya per orang."
    )

    st.markdown("---")

    # Cara menggunakan
    st.subheader("Cara Menggunakan")

    steps = [
        ("📁", "Upload Foto", "Upload file foto langsung, file ZIP, atau paste link Google Drive"),
        ("🔍", "Deteksi Wajah", "Sistem mendeteksi setiap wajah dan mengekstraksi fitur uniknya"),
        ("🧩", "Pengelompokan", "Wajah yang sama dikelompokkan otomatis — 1 cluster = 1 orang"),
        ("📥", "Download", "Pilih cluster yang diinginkan, download sebagai ZIP per orang"),
    ]

    cols = st.columns(4)
    for col, (icon, title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f"<div style='text-align:center; font-size:32px'>{icon}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**{title}**")
            st.caption(desc)

    st.markdown("---")

    # Teknologi
    st.subheader("Teknologi")

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown("**InsightFace**")
    col1.caption("Face Detection & Embedding")
    col2.markdown("**UMAP**")
    col2.caption("Dimensionality Reduction")
    col3.markdown("**HDBSCAN**")
    col3.caption("Density-based Clustering")
    col4.markdown("**Streamlit**")
    col4.caption("Web Interface")

    st.markdown("---")

    # Tombol mulai
    if st.button("🚀 Mulai Pengelompokan", type="primary", use_container_width=True):
        st.session_state.page = "upload"
        st.rerun()

    st.markdown("---")
    st.caption("Skripsi — Ade Nurchalisa · 60200122039 · UIN Alauddin Makassar · 2026")