import logging
import numpy as np
import umap
import hdbscan
from sklearn.metrics import silhouette_score

from src.config import (
    HDBSCAN_CLUSTER_SELECTION_METHOD,
    UMAP_N_COMPONENTS,
    UMAP_N_NEIGHBORS,
    UMAP_MIN_DIST,
    UMAP_RANDOM_STATE,
)

logger = logging.getLogger(__name__)


def get_adaptive_params(n_faces):
    """Parameter HDBSCAN adaptif berdasarkan jumlah wajah."""
    if n_faces < 50:
        return 2, 2
    elif n_faces < 200:
        return 3, 3
    elif n_faces < 500:
        return 5, 5
    elif n_faces < 2000:
        return 8, 8
    elif n_faces < 5000:
        return 12, 12
    else:
        return 20, 20  # optimal dari NB09


def reduce_dimensions(embeddings):
    """Reduksi dimensi dengan UMAP (konfigurasi tetap dari NB09)."""
    n_faces = len(embeddings)

    if n_faces < 15:
        logger.warning(f"Data terlalu kecil untuk UMAP ({n_faces} wajah). Melewati reduksi dimensi.")
        return embeddings

    n_neighbors = min(UMAP_N_NEIGHBORS, n_faces - 1)

    reducer = umap.UMAP(
        n_components=min(UMAP_N_COMPONENTS, n_faces - 1),
        n_neighbors=n_neighbors,
        metric="cosine",
        min_dist=UMAP_MIN_DIST,
        random_state=UMAP_RANDOM_STATE,
        verbose=False,
    )

    logger.info(f"UMAP: {embeddings.shape[1]}D → {UMAP_N_COMPONENTS}D ({n_faces} wajah)")
    return reducer.fit_transform(embeddings)


def cluster_faces(embeddings):
    n_faces = len(embeddings)

    if n_faces < 2:
        return np.array([-1] * n_faces), None, {
            "n_clusters": 0, "n_noise": n_faces,
            "noise_pct": 100.0, "coverage_pct": 0.0, "silhouette": None,
        }

    embeddings_reduced = reduce_dimensions(embeddings)
    min_cluster_size, min_samples = get_adaptive_params(n_faces)

    logger.info(f"HDBSCAN: min_cluster_size={min_cluster_size}, min_samples={min_samples}")

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        cluster_selection_method=HDBSCAN_CLUSTER_SELECTION_METHOD,
    )
    labels = clusterer.fit_predict(embeddings_reduced)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise    = int((labels == -1).sum())
    total      = len(labels)

    metrics = {
        "n_clusters":   n_clusters,
        "n_noise":      n_noise,
        "noise_pct":    round(n_noise / total * 100, 1),
        "coverage_pct": round((total - n_noise) / total * 100, 1),
        "silhouette":   None,
    }

    clustered_mask = labels >= 0
    if n_clusters > 1 and clustered_mask.sum() > n_clusters:
        metrics["silhouette"] = round(
            silhouette_score(embeddings_reduced[clustered_mask], labels[clustered_mask]), 4
        )

    return labels, clusterer, metrics


def run_clustering_pipeline(all_faces, progress_callback=None):
    if not all_faces:
        return {}, [], {
            "n_clusters": 0, "n_noise": 0,
            "noise_pct": 0, "coverage_pct": 0, "silhouette": None,
        }

    if progress_callback:
        progress_callback(1, 3, "Mereduksi dimensi (UMAP)...")

    embeddings = np.array([face["embedding"] for face in all_faces])

    if progress_callback:
        progress_callback(2, 3, "Mengelompokkan wajah (HDBSCAN)...")

    labels, _, metrics = cluster_faces(embeddings)

    if progress_callback:
        progress_callback(3, 3, "Menyusun hasil...")

    clusters    = {}
    noise_faces = []
    for face, label in zip(all_faces, labels):
        label = int(label)
        face["cluster_id"] = label
        if label == -1:
            noise_faces.append(face)
        else:
            clusters.setdefault(label, []).append(face)

    clusters = dict(sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True))
    return clusters, noise_faces, metrics
