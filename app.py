import streamlit as st

# Konfigurasi halaman — HARUS di baris paling pertama
st.set_page_config(
    page_title="FaceCluster",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
import os
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session state initialization
defaults = {
    "page": "overview",
    "photos": None,
    "clusters": None,
    "noise_faces": None,
    "metrics": None,
    "face_stats": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Sidebar
from components.sidebar import render_sidebar
render_sidebar()

# Router
from components.page_overview import render as overview
from components.page_upload import render as upload
from components.page_processing import render as processing
from components.page_results import render as results

pages = {
    "overview": overview,
    "upload": upload,
    "processing": processing,
    "results": results,
}

# Render halaman aktif
current_page = st.session_state.page
if current_page in pages:
    pages[current_page]()
else:
    st.session_state.page = "overview"
    st.rerun()