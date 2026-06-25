import streamlit as st


def render_topnav():
    """Navigasi atas FotoQu (menggantikan sidebar yang di-collapse).

    Brand + baris tombol navigasi horizontal + status ringkas pemrosesan.
    Logika navigasi identik dengan sidebar lama: set st.session_state.page lalu rerun.
    """
    # ── Brand bar ──
    st.markdown("""
    <div style="display:flex; align-items:baseline; gap:10px; margin:4px 0 14px 0;">
        <span style="font-size:1.7rem; font-family:'DM Serif Display',serif;
                     font-weight:400; color:#141414;">FotoQu</span>
        <span style="font-size:0.72rem; letter-spacing:2px; text-transform:uppercase;
                     color:#C27D2A; font-weight:600;">Sort photos by face</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Navigasi horizontal ──
    pages = {
        "overview":   ("ℹ️",  "Overview"),
        "upload":     ("📁",  "Upload"),
        "processing": ("⏳",  "Processing"),
        "results":    ("📊",  "Hasil"),
    }

    current = st.session_state.page
    nav_cols = st.columns(len(pages))
    for col, (key, (icon, label)) in zip(nav_cols, pages.items()):
        with col:
            is_active = current == key
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = key
                st.rerun()

    # ── Status ringkas ──
    photos     = st.session_state.get("photos")
    clusters   = st.session_state.get("clusters")
    face_stats = st.session_state.get("face_stats")

    if photos or clusters:
        parts = []
        if photos:
            parts.append(f"📷 {len(photos)} foto dimuat")
        if face_stats:
            parts.append(f"👤 {face_stats['total_faces']} wajah terdeteksi")
        if clusters:
            parts.append(f"👥 {len(clusters)} cluster terbentuk")
        st.markdown(
            "<p style='color:#666666; font-size:0.8rem; margin:6px 0 0 0;'>"
            + "&nbsp;&nbsp;·&nbsp;&nbsp;".join(parts)
            + "</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<hr style='border:none; border-top:1px solid #E7E0D4; margin:14px 0 18px 0;'>",
        unsafe_allow_html=True,
    )
