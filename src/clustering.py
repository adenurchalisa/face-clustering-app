import logging
import numpy as np
import hdbscan
from sklearn.metrics import silhouette_score

from src.config import (
    HDBSCAN_MIN_CLUSTER_SIZE, HDBSCAN_MIN_SAMPLES,
    HDBSCAN_CLUSTER_SELECTION_METHOD, HDBSCAN_METRIC,
)

logger = logging.getLogger(__name__)


def cluster_faces(embeddings):
    if len(embeddings) < 2:
        return np.array([-1] * len(embeddings)), None, {
            "n_clusters": 0,
            "n_noise": len(embeddings),
            "noise_pct": 100.0,
            "coverage_pct": 0.0,
            "silhouette": None,
        }

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=HDBSCAN_MIN_CLUSTER_SIZE,
        min_samples=HDBSCAN_MIN_SAMPLES,
        cluster_selection_method=HDBSCAN_CLUSTER_SELECTION_METHOD,
        metric=HDBSCAN_METRIC,
    )
    labels = clusterer.fit_predict(embeddings)

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
            silhouette_score(embeddings[clustered_mask], labels[clustered_mask]), 4
        )

    return labels, clusterer, metrics


def run_clustering_pipeline(all_faces, progress_callback=None):
    if not all_faces:
        return {}, [], {
            "n_clusters": 0, "n_noise": 0,
            "noise_pct": 0, "coverage_pct": 0, "silhouette": None,
        }

    if progress_callback:
        progress_callback(1, 2, "Mengelompokkan wajah (HDBSCAN)...")

    embeddings = np.array([face["embedding"] for face in all_faces])
    labels, _, metrics = cluster_faces(embeddings)

    if progress_callback:
        progress_callback(2, 2, "Menyusun hasil...")

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
