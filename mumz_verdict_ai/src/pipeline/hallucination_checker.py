"""Stage 6 — Verify each verdict claim is grounded in source reviews."""

from typing import Dict, List, Tuple

import numpy as np

from models.embeddings import cosine_similarity_pair, get_embeddings
from schemas.claim_schema import FinalVerdict

# A claim must hit at least this similarity to one review to be considered grounded.
GROUNDING_THRESHOLD = 0.35


def _max_similarity_to_reviews(
    claim_emb: np.ndarray,
    review_embeddings: np.ndarray,
) -> float:
    return max(cosine_similarity_pair(claim_emb, rev) for rev in review_embeddings)


def check_claim_grounding(
    claim_text: str,
    review_embeddings: np.ndarray,
) -> Tuple[bool, float]:
    """Return (is_grounded, best_similarity_score)."""
    claim_emb = get_embeddings([claim_text])[0]
    score = _max_similarity_to_reviews(claim_emb, review_embeddings)
    return score >= GROUNDING_THRESHOLD, score


def run_hallucination_check(
    verdict: FinalVerdict,
    reviews: List[Dict],
) -> FinalVerdict:
    """
    For every verdict item, check semantic similarity against source reviews.
    Claims below GROUNDING_THRESHOLD are appended to verdict.hallucination_flags.
    """
    review_texts = [r["text"] for r in reviews]
    print(f"[hallucination] Embedding {len(review_texts)} reviews...")
    review_embeddings = get_embeddings(review_texts)

    flagged: List[str] = []
    for item in verdict.verdict_items:
        grounded, score = check_claim_grounding(item.claim, review_embeddings)
        status = "OK " if grounded else "FLAG"
        print(f"[hallucination] [{status}] sim={score:.3f}  {item.claim[:70]}")
        if not grounded:
            flagged.append(item.claim)

    verdict.hallucination_flags = flagged
    print(f"[hallucination] {len(flagged)} claim(s) flagged out of {len(verdict.verdict_items)}")
    return verdict
