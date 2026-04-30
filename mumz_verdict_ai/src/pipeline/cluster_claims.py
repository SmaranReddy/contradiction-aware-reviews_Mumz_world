"""Stage 3 — Cluster semantically similar claims."""

from typing import Dict, List

from sklearn.cluster import AgglomerativeClustering

from models.embeddings import get_embeddings
from schemas.claim_schema import Claim, ClusterSummary
from pipeline.confidence_scoring import compute_agreement_ratio


def cluster_claims(
    claims: List[Claim],
    distance_threshold: float = 0.45,
) -> Dict[int, List[Claim]]:
    """
    Group claims by semantic similarity using agglomerative clustering.
    distance_threshold controls granularity — lower = more clusters.
    Returns {cluster_id: [Claim, ...]}.
    """
    if len(claims) < 2:
        return {0: claims}

    texts = [c.claim for c in claims]
    embeddings = get_embeddings(texts)

    model = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="cosine",
        linkage="average",
    )
    labels = model.fit_predict(embeddings)

    clusters: Dict[int, List[Claim]] = {}
    for claim, label in zip(claims, labels):
        clusters.setdefault(int(label), []).append(claim)

    print(f"[cluster] {len(claims)} claims → {len(clusters)} clusters")
    return clusters


def summarize_clusters(clusters: Dict[int, List[Claim]]) -> List[ClusterSummary]:
    """Wrap each cluster into a ClusterSummary (contradiction flag filled later)."""
    summaries = []
    for cluster_id, claims in clusters.items():
        aspects = [c.aspect for c in claims]
        dominant_aspect = max(set(aspects), key=aspects.count)
        summaries.append(
            ClusterSummary(
                cluster_id=cluster_id,
                aspect=dominant_aspect,
                claims=claims,
                has_contradiction=False,
                agreement_ratio=compute_agreement_ratio(claims),
            )
        )
    return summaries
