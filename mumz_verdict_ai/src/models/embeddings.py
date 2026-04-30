"""
Embedding utilities.
Prefers sentence-transformers (all-MiniLM-L6-v2).
Falls back to TF-IDF if sentence-transformers is not installed.
"""

from typing import List

import numpy as np


def get_embeddings(texts: List[str]) -> np.ndarray:
    """
    Return a (N, D) float32 array of L2-normalised embeddings.
    Tries sentence-transformers first, then TF-IDF fallback.
    """
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    except ImportError:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.preprocessing import normalize

        vec = TfidfVectorizer(max_features=512, stop_words="english")
        matrix = vec.fit_transform(texts).toarray().astype(np.float32)
        return normalize(matrix)


def cosine_similarity_pair(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1-D vectors."""
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0


def cosine_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """Pairwise cosine similarities for a batch of normalised embeddings."""
    return (embeddings @ embeddings.T).astype(np.float32)
