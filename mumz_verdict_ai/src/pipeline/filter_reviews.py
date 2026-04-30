"""Stage 1 — Load and filter raw reviews."""

import json
import re
from typing import List, Dict


def load_reviews(path: str) -> List[Dict]:
    """Load reviews from a JSON file. Expected shape: [{"id": str, "text": str}, ...]."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.encode("ascii", errors="ignore").decode()  # drop non-ASCII
    return text


def filter_reviews(reviews: List[Dict], min_words: int = 10) -> List[Dict]:
    """
    Clean and filter reviews.
    Drops reviews with fewer than min_words words after cleaning.
    Mutates 'text' in place on each review dict.
    """
    kept = []
    for r in reviews:
        r["text"] = _clean_text(r.get("text", ""))
        if len(r["text"].split()) >= min_words:
            kept.append(r)

    print(f"[filter] {len(kept)}/{len(reviews)} reviews passed (min_words={min_words})")
    return kept
