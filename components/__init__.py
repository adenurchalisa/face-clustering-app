import streamlit as st
from src.utils import cleanup_temp


def reset_session_state():
    """Reset semua session state terkait pemrosesan foto dan bersihkan file temporer."""
    for key in ["photos", "clusters", "noise_faces", "metrics", "face_stats"]:
        st.session_state[key] = None
    cleanup_temp()
