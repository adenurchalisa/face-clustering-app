import logging
import numpy as np
import umap
import hdbscan

logger = logging.getLogger(__name__)
from sklearn.metrics import silhouette_score
from src.config import (
    UMAP_N_COMPONENTS, UMAP_N_NEIGHBORS, UMAP_MIN_DIST,
    UMAP_METRIC, UMAP_RANDOM_STATE,
    HDBSCAN_MIN_CLUSTER_SIZE, HDBSCAN_MIN_SAMPLES,
    HDBSCAN_CLUSTER_SELECTION_METHOD,
)

def reduce_dimensions(embeddings):
    n_samples = len(embeddings)
    if n_samples < 2:
        return embeddings, None
    n_neighbors = min(UMAP_N_NEIGHBORS, n_samples - 1)
   
    reducer = umap.UMAP(
        n_components=UMAP_N_COMPONENTS,
        n_neighbors=n_neighbors,
        min_dist=UMAP_MIN_DIST,
        metric=UMAP_METRIC,
        random_state=UMAP_RANDOM_STATE,
    )
    reduced = reducer.fit_transform(embeddings)
    return reduced, reducer

def cluster_faces(reduced_embeddings):
    if len(reduced_embeddings) < 2:
        return np.array([-1] * len(reduced_embeddings)), None, {
            "n_clusters": 0,
            "n_noise": len(reduced_embeddings),
            "noise_pct": 100.0,
            "coverage_pct": 0.0,
            "silhouette": None,
        }
        
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=HDBSCAN_MIN_CLUSTER_SIZE,
        min_samples=HDBSCAN_MIN_SAMPLES,
        cluster_selection_method=HDBSCAN_CLUSTER_SELECTION_METHOD,
    )
    labels = clusterer.fit_predict(reduced_embeddings)
    
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
        metrics["silhouette"] = round(silhouette_score(reduced_embeddings[clustered_mask], labels[clustered_mask]), 4)
    
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
        progress_callback(1, 3, "Mereduksi dimensi (UMAP)...")
        
    embeddings = np.array([face["embedding"] for face in all_faces])
    reduced, _ = reduce_dimensions(embeddings)
    
    if progress_callback:
        progress_callback(2, 3, "Mengelompokkan wajah (HDBSCAN)...")
        
    labels, _, metrics = cluster_faces(reduced)
    
    if progress_callback:
        progress_callback(3, 3, "Menyusun hasil...")
        
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