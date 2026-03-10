import streamlit as st
from src.utils import create_cluster_zip, numpy_to_pil
from src.config import MAX_CLUSTER_PREVIEW, MAX_NOISE_PREVIEW
from components import reset_session_state


def render():
    clusters   = st.session_state.get("clusters")
    metrics    = st.session_state.get("metrics")
    noise_faces = st.session_state.get("noise_faces", [])

    if not clusters:
        st.warning("Belum ada hasil clustering.")
        if st.button("← Upload Foto"):
            st.session_state.page = "upload"
            st.rerun()
        return

    # ── Header ──
    st.markdown("""
    <div style="margin-bottom: 8px;">
        <h2 style="font-weight:800; color:#0F172A; margin:0;">📊 Hasil Pengelompokan</h2>
        <p style="color:#64748B; margin:4px 0 0 0; font-size:0.9rem;">
            Wajah berhasil dideteksi dan dikelompokkan secara otomatis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrik utama ──
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    col1.metric("👥 Cluster", metrics["n_clusters"])
    col2.metric("✅ Coverage", f"{metrics['coverage_pct']}%")
    col3.metric("🔇 Noise", f"{metrics['noise_pct']}%")
    col4.metric("📐 Silhouette", metrics.get("silhouette") or "N/A")

    st.markdown("---")

    # ── Multi-select download ──
    cluster_ids = list(clusters.keys())
    cluster_options = {
        f"Cluster {cid + 1}  ({len(clusters[cid])} wajah)": cid
        for cid in cluster_ids
    }

    st.markdown("#### 📦 Download Batch")
    selected_labels = st.multiselect(
        "Pilih cluster untuk diunduh sekaligus:",
        options=list(cluster_options.keys()),
        help="Pilih satu atau lebih cluster, lalu klik tombol download",
    )

    if selected_labels:
        selected_ids = [cluster_options[label] for label in selected_labels]
        zip_buffer   = create_cluster_zip(clusters, selected_ids)

        col_info, col_dl = st.columns([3, 1])
        with col_info:
            st.info(f"{len(selected_ids)} cluster dipilih · siap diunduh")
        with col_dl:
            st.download_button(
                label="⬇️ Download ZIP",
                data=zip_buffer,
                file_name="facecluster_results.zip",
                mime="application/zip",
            )

    st.markdown("---")
    st.markdown("#### 👤 Gallery per Cluster")

    # ── Gallery per cluster ──
    for cid in cluster_ids:
        faces         = clusters[cid]
        unique_photos = len(set(f["source_photo"] for f in faces))

        with st.expander(
            f"Cluster {cid + 1} — {len(faces)} wajah · {unique_photos} foto",
            expanded=(cid == cluster_ids[0]),
        ):
            col_info2, col_dl2 = st.columns([3, 1])
            with col_info2:
                st.markdown(
                    f"<p style='color:#64748B; font-size:0.85rem; margin:4px 0;'>"
                    f"Orang yang sama muncul di <b>{unique_photos}</b> foto</p>",
                    unsafe_allow_html=True,
                )
            with col_dl2:
                single_zip = create_cluster_zip(clusters, [cid])
                st.download_button(
                    label=f"⬇️ Download",
                    data=single_zip,
                    file_name=f"cluster_{cid + 1}.zip",
                    mime="application/zip",
                    key=f"dl_{cid}",
                )

            cols = st.columns(6)
            for i, face in enumerate(faces[:MAX_CLUSTER_PREVIEW]):
                with cols[i % 6]:
                    st.image(numpy_to_pil(face["crop"]), use_container_width=True)

            if len(faces) > MAX_CLUSTER_PREVIEW:
                st.caption(f"Menampilkan {MAX_CLUSTER_PREVIEW} dari {len(faces)} wajah")

    # ── Noise section ──
    if noise_faces:
        st.markdown("---")
        with st.expander(f"🔇 Tidak Terkelompok — {len(noise_faces)} wajah"):
            st.markdown(
                "<p style='color:#94A3B8; font-size:0.85rem;'>"
                "Wajah-wajah ini tidak masuk ke cluster manapun — "
                "biasanya hanya muncul sekali atau kualitas deteksinya rendah."
                "</p>",
                unsafe_allow_html=True,
            )
            cols = st.columns(6)
            for i, face in enumerate(noise_faces[:MAX_NOISE_PREVIEW]):
                with cols[i % 6]:
                    st.image(numpy_to_pil(face["crop"]), use_container_width=True)

            if len(noise_faces) > MAX_NOISE_PREVIEW:
                st.caption(f"Menampilkan {MAX_NOISE_PREVIEW} dari {len(noise_faces)} wajah")

    # ── Reset ──
    st.markdown("---")
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("🔄  Proses Foto Baru", use_container_width=True):
            reset_session_state()
            st.session_state.page = "upload"
            st.rerun()
