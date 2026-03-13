import os
import cv2
import streamlit as st
from src.utils import create_cluster_zip, numpy_to_pil
from src.config import MAX_CLUSTER_PREVIEW, MAX_NOISE_PREVIEW
from components import reset_session_state


def _load_full_photo(path):
    """Baca foto penuh sebagai PIL Image (RGB)."""
    img = cv2.imread(path)
    if img is None:
        return None
    return numpy_to_pil(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def render():
    clusters = st.session_state.get("clusters")
    metrics = st.session_state.get("metrics")
    noise_faces = st.session_state.get("noise_faces", [])

    if not clusters:
        st.warning("Belum ada hasil clustering.")
        if st.button("← Upload Foto"):
            st.session_state.page = "upload"
            st.rerun()
        return

    st.header("📊 Hasil Pengelompokan")

    # Metrik utama
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cluster", metrics["n_clusters"])
    col2.metric("Coverage", f"{metrics['coverage_pct']}%")
    col3.metric("Noise", f"{metrics['noise_pct']}%")
    col4.metric("Silhouette", metrics.get("silhouette") or "N/A")

    st.markdown("---")

    # Multi-select download
    cluster_ids = list(clusters.keys())
    cluster_options = {
        f"Cluster {cid + 1} ({len(set(f['source_photo'] for f in clusters[cid]))} foto)": cid
        for cid in cluster_ids
    }

    selected_labels = st.multiselect(
        "Pilih cluster untuk download:",
        options=list(cluster_options.keys()),
        help="Pilih satu atau lebih cluster, lalu klik tombol download",
    )

    if selected_labels:
        selected_ids = [cluster_options[label] for label in selected_labels]
        zip_buffer = create_cluster_zip(clusters, selected_ids)

        col_dl1, col_dl2 = st.columns([3, 1])
        with col_dl1:
            st.info(f"{len(selected_ids)} cluster dipilih")
        with col_dl2:
            st.download_button(
                label="↓ Download ZIP",
                data=zip_buffer,
                file_name="facecluster_results.zip",
                mime="application/zip",
                type="primary",
            )

    st.markdown("---")

    # Gallery per cluster
    for cid in cluster_ids:
        faces = clusters[cid]
        unique_photo_paths = list(dict.fromkeys(f["source_photo"] for f in faces))

        # Wajah representatif: skor deteksi tertinggi
        rep_face = max(faces, key=lambda f: f["det_score"])

        with st.expander(
            f"👤 Cluster {cid + 1} — {len(faces)} wajah dari {len(unique_photo_paths)} foto",
            expanded=(cid == cluster_ids[0]),
        ):
            # Baris atas: thumbnail wajah representatif + info + tombol download
            col_rep, col_info = st.columns([1, 5])
            with col_rep:
                st.image(
                    numpy_to_pil(rep_face["crop"]),
                    width=100,
                    caption="Representatif",
                )
            with col_info:
                st.caption(
                    f"Wajah ini muncul di {len(unique_photo_paths)} foto. "
                    f"Skor deteksi terbaik: {rep_face['det_score']:.2f}"
                )
                single_zip = create_cluster_zip(clusters, [cid])
                st.download_button(
                    label=f"↓ Download Cluster {cid + 1}",
                    data=single_zip,
                    file_name=f"cluster_{cid + 1}.zip",
                    mime="application/zip",
                    key=f"dl_{cid}",
                )

            st.caption("Foto-foto yang mengandung wajah ini:")

            # Grid foto penuh (bukan crop wajah)
            cols = st.columns(3)
            shown = 0
            for i, path in enumerate(unique_photo_paths[:MAX_CLUSTER_PREVIEW]):
                img_pil = _load_full_photo(path)
                if img_pil is None:
                    continue
                with cols[shown % 3]:
                    st.image(
                        img_pil,
                        use_container_width=True,
                        caption=os.path.basename(path),
                    )
                shown += 1

            if len(unique_photo_paths) > MAX_CLUSTER_PREVIEW:
                st.caption(
                    f"Menampilkan {MAX_CLUSTER_PREVIEW} dari {len(unique_photo_paths)} foto"
                )

    # Noise section
    if noise_faces:
        st.markdown("---")
        with st.expander(f"🔇 Noise — {len(noise_faces)} wajah tidak terkelompok"):
            st.caption(
                "Wajah-wajah ini tidak masuk ke cluster manapun. "
                "Bisa karena hanya muncul sekali atau kualitas deteksi rendah."
            )
            cols = st.columns(6)
            for i, face in enumerate(noise_faces[:MAX_NOISE_PREVIEW]):
                with cols[i % 6]:
                    pil_img = numpy_to_pil(face["crop"])
                    st.image(pil_img, use_container_width=True)

            if len(noise_faces) > MAX_NOISE_PREVIEW:
                st.caption(f"Menampilkan {MAX_NOISE_PREVIEW} dari {len(noise_faces)} wajah noise")

    # Reset
    st.markdown("---")
    if st.button("🔄 Proses Foto Baru", use_container_width=True):
        reset_session_state()
        st.session_state.page = "upload"
        st.rerun()
