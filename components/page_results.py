import base64
import html
import io
import os
import cv2
import streamlit as st
from src.utils import create_cluster_zip, numpy_to_pil
from src.config import (
    MAX_CLUSTER_PREVIEW,
    GALLERY_PREVIEW_INITIAL,
    GALLERY_THUMB_MAX_DIM,
    GALLERY_JPEG_QUALITY,
    MAX_NOISE_PREVIEW,
)
from components import reset_session_state


@st.cache_data(show_spinner=False)
def _load_full_photo(path, max_dim=GALLERY_THUMB_MAX_DIM):
    """Baca foto penuh sebagai PIL Image (RGB), dengan downscale untuk preview."""
    img = cv2.imread(path)
    if img is None:
        return None
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w = max(1, int(round(w * scale)))
        new_h = max(1, int(round(h * scale)))
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return numpy_to_pil(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def _pil_to_data_uri(img_pil, quality=GALLERY_JPEG_QUALITY):
    """Encode PIL Image (RGB) jadi data-URI JPEG base64.

    Gambar di-embed langsung di HTML sebagai data-URI agar TIDAK lewat
    MediaFileManager Streamlit — manager itu meng-GC media antar-rerun, yang pada
    galeri besar (puluhan cluster x ratusan foto) bikin sebagian gambar 404/blank
    saat halaman dibuka ulang. Data-URI tidak pernah ter-GC, jadi selalu tampil.
    """
    buf = io.BytesIO()
    img_pil.save(buf, format="JPEG", quality=quality)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def _render_image_grid(items, columns=3, show_caption=True):
    """Render grid gambar dari list (img_pil, caption) sebagai satu blok HTML base64."""
    cells = []
    for img_pil, caption in items:
        uri = _pil_to_data_uri(img_pil)
        cap_html = ""
        if show_caption and caption:
            cap_html = (
                f'<span style="font-size:0.72rem;color:#64748B;text-align:center;'
                f'word-break:break-all;margin-top:4px;">{html.escape(caption)}</span>'
            )
        cells.append(
            '<div style="display:flex;flex-direction:column;align-items:center;">'
            f'<img src="{uri}" loading="lazy" '
            'style="width:100%;border-radius:8px;display:block;object-fit:cover;"/>'
            f'{cap_html}</div>'
        )
    grid = (
        f'<div style="display:grid;grid-template-columns:repeat({columns},1fr);gap:12px;">'
        + "".join(cells)
        + "</div>"
    )
    st.markdown(grid, unsafe_allow_html=True)


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
        f"Cluster {cid + 1} ({len(set(f['source_photo'] for f in clusters[cid]))} foto)": cid
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
                label="↓ Download ZIP",
                data=zip_buffer,
                file_name="facecluster_results.zip",
                mime="application/zip",
            )

    st.markdown("---")
    st.markdown("#### 👤 Gallery per Cluster")

    # ── Gallery per cluster ──
    # Expander dibuat lazy (on_change="rerun" + cek .open): tanpa ini, isi SEMUA
    # expander (thumbnail, build ZIP, load+render semua foto) dieksekusi di SETIAP
    # render walau sedang collapsed — dengan puluhan cluster ini bikin halaman berat
    # dan sebagian elemen (termasuk thumbnail representatif) gagal sempat tergambar.
    for cid in cluster_ids:
        faces = clusters[cid]
        unique_photo_paths = list(dict.fromkeys(f["source_photo"] for f in faces))

        exp = st.expander(
            f"👤 Cluster {cid + 1} — {len(faces)} wajah dari {len(unique_photo_paths)} foto",
            expanded=(cid == cluster_ids[0]),
            key=f"cluster_expander_{cid}",
            on_change="rerun",
        )
        with exp:
            if not exp.open:
                st.caption("Klik untuk memuat detail cluster ini.")
                continue

            # Wajah representatif: skor deteksi tertinggi
            rep_face = max(faces, key=lambda f: f["det_score"])

            # Baris atas: thumbnail wajah representatif + info + tombol download
            col_rep, col_info = st.columns([1, 5])
            with col_rep:
                rep_uri = _pil_to_data_uri(numpy_to_pil(rep_face["crop"]))
                st.markdown(
                    f'<img src="{rep_uri}" width="100" '
                    'style="border-radius:8px;display:block;"/>'
                    '<span style="font-size:0.72rem;color:#64748B;">Representatif</span>',
                    unsafe_allow_html=True,
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

            # Batasi jumlah foto awal; user bisa "tampilkan semua" sampai MAX_CLUSTER_PREVIEW.
            # Membatasi jumlah gambar yang di-embed menjaga ukuran HTML & beban render.
            show_all_key = f"show_all_{cid}"
            show_all = st.session_state.get(show_all_key, False)
            limit = MAX_CLUSTER_PREVIEW if show_all else GALLERY_PREVIEW_INITIAL
            paths_to_show = unique_photo_paths[:limit]

            # Grid foto penuh (bukan crop wajah), di-embed sebagai base64 data-URI
            with st.spinner("Memuat foto..."):
                loaded_photos = [
                    (img_pil, os.path.basename(path))
                    for path in paths_to_show
                    if (img_pil := _load_full_photo(path)) is not None
                ]
            _render_image_grid(loaded_photos, columns=3)

            total = len(unique_photo_paths)
            if not show_all and total > GALLERY_PREVIEW_INITIAL:
                st.caption(f"Menampilkan {len(paths_to_show)} dari {total} foto")
                if st.button(
                    f"Tampilkan semua {min(total, MAX_CLUSTER_PREVIEW)} foto",
                    key=f"more_{cid}",
                ):
                    st.session_state[show_all_key] = True
                    st.rerun()
            elif total > MAX_CLUSTER_PREVIEW:
                st.caption(f"Menampilkan {MAX_CLUSTER_PREVIEW} dari {total} foto")

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
            noise_items = [
                (numpy_to_pil(face["crop"]), None)
                for face in noise_faces[:MAX_NOISE_PREVIEW]
            ]
            _render_image_grid(noise_items, columns=6, show_caption=False)

            if len(noise_faces) > MAX_NOISE_PREVIEW:
                st.caption(f"Menampilkan {MAX_NOISE_PREVIEW} dari {len(noise_faces)} wajah")

    # ── Reset ──
    st.markdown("---")
    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        if st.button("🔄 Proses Foto Baru", use_container_width=True):
            reset_session_state()
            st.session_state.page = "upload"
            st.rerun()
