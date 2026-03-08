import streamlit as st
from src.utils import create_cluster_zip, numpy_to_pil


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
        f"Cluster {cid + 1} ({len(clusters[cid])} wajah)": cid
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
                label=f"↓ Download ZIP",
                data=zip_buffer,
                file_name="facecluster_results.zip",
                mime="application/zip",
                type="primary",
            )

    st.markdown("---")

    # Gallery per cluster
    for cid in cluster_ids:
        faces = clusters[cid]
        unique_photos = len(set(f["source_photo"] for f in faces))

        with st.expander(
            f"👤 Cluster {cid + 1} — {len(faces)} wajah dari {unique_photos} foto",
            expanded=(cid == cluster_ids[0]),  # Cluster pertama dibuka otomatis
        ):
            # Download per cluster
            single_zip = create_cluster_zip(clusters, [cid])
            st.download_button(
                label=f"↓ Download Cluster {cid + 1}",
                data=single_zip,
                file_name=f"cluster_{cid + 1}.zip",
                mime="application/zip",
                key=f"dl_{cid}",
            )

            # Grid wajah
            max_preview = 18
            cols = st.columns(6)
            for i, face in enumerate(faces[:max_preview]):
                with cols[i % 6]:
                    pil_img = numpy_to_pil(face["crop"])
                    st.image(pil_img, use_container_width=True)

            if len(faces) > max_preview:
                st.caption(f"Menampilkan {max_preview} dari {len(faces)} wajah")

    # Noise section
    if noise_faces:
        st.markdown("---")
        with st.expander(f"🔇 Noise — {len(noise_faces)} wajah tidak terkelompok"):
            st.caption(
                "Wajah-wajah ini tidak masuk ke cluster manapun. "
                "Bisa karena hanya muncul sekali atau kualitas deteksi rendah."
            )
            cols = st.columns(6)
            for i, face in enumerate(noise_faces[:12]):
                with cols[i % 6]:
                    pil_img = numpy_to_pil(face["crop"])
                    st.image(pil_img, use_container_width=True)

            if len(noise_faces) > 12:
                st.caption(f"Menampilkan 12 dari {len(noise_faces)} wajah noise")

    # Reset
    st.markdown("---")
    if st.button("🔄 Proses Foto Baru", use_container_width=True):
        for key in ["photos", "clusters", "noise_faces", "metrics", "face_stats"]:
            st.session_state[key] = None
        st.session_state.page = "upload"
        st.rerun()