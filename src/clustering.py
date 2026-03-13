import logging
import numpy as np
import hdbscan
from sklearn.preprocessing import normalize
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)

from src.config import (
    HDBSCAN_MIN_CLUSTER_SIZE, HDBSCAN_MIN_SAMPLES,
    HDBSCAN_CLUSTER_SELECTION_METHOD,
)


def cluster_faces(embeddings):
    n_samples = len(embeddings)

    if n_samples < 2:
        return np.array([-1] * n_samples), None, {
            "n_clusters": 0,
            "n_noise": n_samples,
            "noise_pct": 100.0,
            "coverage_pct": 0.0,
            "silhouette": None,
        }

    # Normalisasi L2 agar cosine distance setara euclidean distance
    normed = normalize(embeddings, norm="l2")

    # Parameter adaptif terhadap ukuran dataset
    min_cluster_size = max(2, min(HDBSCAN_MIN_CLUSTER_SIZE, n_samples // 5))
    min_samples = max(1, min(HDBSCAN_MIN_SAMPLES, min_cluster_size))

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        cluster_selection_method=HDBSCAN_CLUSTER_SELECTION_METHOD,
        metric="euclidean",
    )
    labels = clusterer.fit_predict(normed)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int((labels == -1).sum())
    total = len(labels)

    metrics = {
        "n_clusters": n_clusters,
        "n_noise": n_noise,
        "noise_pct": round(n_noise / total * 100, 1),
        "coverage_pct": round((total - n_noise) / total * 100, 1),
        "silhouette": None,
    }

    clustered_mask = labels >= 0
    if n_clusters > 1 and clustered_mask.sum() > n_clusters:
        metrics["silhouette"] = round(
            silhouette_score(normed[clustered_mask], labels[clustered_mask]), 4
        )

    return labels, clusterer, metrics


def run_clustering_pipeline(all_faces, progress_callback=None):
    if not all_faces:
        return {}, [], {
            "n_clusters": 0,
            "n_noise": 0,
            "noise_pct": 0,
            "coverage_pct": 0,
            "silhouette": None,
        }

    if progress_callback:
        progress_callback(1, 2, "Mengelompokkan wajah (HDBSCAN)...")

    embeddings = np.array([face["embedding"] for face in all_faces])
    labels, _, metrics = cluster_faces(embeddings)

    if progress_callback:
        progress_callback(2, 2, "Menyusun hasil...")

    clusters = {}
    noise_faces = []
    for face, label in zip(all_faces, labels):
        label = int(label)
        face["cluster_id"] = label
        if label == -1:
            noise_faces.append(face)
        else:
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(face)

    clusters = dict(sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True))

    return clusters, noise_faces, metrics
