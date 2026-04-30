"""Stage 2 — Extract structured claims from each review via LLM."""

from typing import List, Dict

from models.llm import chat_completion, parse_json_response
from schemas.claim_schema import Claim

_SYSTEM = """You are a product review analyst. Extract factual claims from the review below.

Return ONLY valid JSON with this shape:
{
  "claims": [
    {
      "claim": "<concise factual statement>",
      "aspect": "<one of: quality, value, durability, safety, ease_of_use, design, size, shipping, customer_service, other>",
      "polarity": <-1 | 0 | 1>
    }
  ]
}

Rules:
- Extract 1–5 claims maximum.
- Each claim must be directly supported by the review text.
- polarity: 1 = positive, -1 = negative, 0 = neutral/mixed.
- Be specific. Avoid vague phrases like "it's good"."""


def _extract_from_review(review: Dict) -> List[Claim]:
    prompt = f"Review ID: {review['id']}\n\n{review['text']}"
    try:
        raw = chat_completion(prompt, system=_SYSTEM, json_mode=True, temperature=0.1)
        data = parse_json_response(raw)
        claims = []
        for c in data.get("claims", []):
            try:
                claims.append(
                    Claim(
                        claim=c["claim"],
                        aspect=c.get("aspect", "other"),
                        polarity=int(c.get("polarity", 0)),
                        review_id=str(review["id"]),
                    )
                )
            except Exception:
                continue
        return claims
    except Exception as e:
        print(f"[extract] Error on review {review['id']}: {e}")
        return []


def extract_all_claims(reviews: List[Dict], log_every: int = 20) -> List[Claim]:
    """
    Run claim extraction over every review.
    Prints progress every log_every reviews.
    """
    all_claims: List[Claim] = []
    for i, review in enumerate(reviews, 1):
        all_claims.extend(_extract_from_review(review))
        if i % log_every == 0:
            print(f"[extract] {i}/{len(reviews)} reviews → {len(all_claims)} claims")

    print(f"[extract] Done. Total claims: {len(all_claims)}")
    return all_claims
