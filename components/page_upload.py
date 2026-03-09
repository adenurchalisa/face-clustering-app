import streamlit as st
from src.utils import save_uploaded_files
from src.drive_handler import download_from_drive
from src.config import MAX_PHOTOS_UPLOAD
from components import reset_session_state


def render():
    st.header("📁 Upload Foto")
    st.caption(f"Maksimal {MAX_PHOTOS_UPLOAD} foto · Format: JPG, PNG, HEIC · Bisa upload ZIP")

    tab1, tab2 = st.tabs(["📁 Upload File", "🔗 Google Drive"])

    with tab1:
        uploaded_files = st.file_uploader(
            "Pilih foto atau file ZIP",
            type=["jpg", "jpeg", "png", "heic", "heif", "zip"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            st.info(f"{len(uploaded_files)} file dipilih")

            # Preview beberapa foto
            preview_cols = st.columns(5)
            for i, f in enumerate(uploaded_files[:5]):
                if not f.name.lower().endswith(".zip"):
                    with preview_cols[i]:
                        try:
                            st.image(f, use_container_width=True)
                        except Exception:
                            st.caption(f.name)

            if len(uploaded_files) > 5:
                st.caption(f"... dan {len(uploaded_files) - 5} file lainnya")

            if st.button("🔄 Proses Foto", type="primary", use_container_width=True, key="btn_upload"):
                with st.spinner("Menyimpan file..."):
                    photo_paths = save_uploaded_files(uploaded_files)

                if not photo_paths:
                    st.error("Tidak ada foto valid yang ditemukan")
                else:
                    st.success(f"{len(photo_paths)} foto siap diproses")
                    reset_session_state()
                    st.session_state.photos = photo_paths
                    st.session_state.page = "processing"
                    st.rerun()

    with tab2:
        st.markdown(
            "Paste link folder Google Drive yang berisi foto. "
            "Pastikan folder di-set **'Anyone with the link'** agar bisa diakses."
        )

        drive_link = st.text_input(
            "Link Google Drive",
            placeholder="https://drive.google.com/drive/folders/...",
        )

        if drive_link:
            if st.button("🔄 Download & Proses", type="primary", use_container_width=True, key="btn_drive"):
                with st.spinner("Mengunduh dari Google Drive..."):
                    photo_paths, error = download_from_drive(drive_link)

                if error:
                    st.error(error)
                elif not photo_paths:
                    st.warning("Tidak ada foto yang ditemukan di link tersebut")
                else:
                    st.success(f"{len(photo_paths)} foto berhasil diunduh")
                    reset_session_state()
                    st.session_state.photos = photo_paths
                    st.session_state.page = "processing"
                    st.rerun()