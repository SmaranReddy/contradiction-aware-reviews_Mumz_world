"""Confidence scoring for claim clusters."""

from typing import List, Literal

from schemas.claim_schema import Claim


def compute_agreement_ratio(claims: List[Claim]) -> float:
    """
    Fraction of claims that share the dominant (positive or negative) polarity.
    Neutral claims (polarity=0) count against agreement.
    Returns 0.0 for empty clusters or all-neutral clusters.
    """
    if not claims:
        return 0.0
    pos = sum(1 for c in claims if c.polarity == 1)
    neg = sum(1 for c in claims if c.polarity == -1)
    return max(pos, neg) / len(claims)


def compute_confidence(
    cluster_claims: List[Claim],
    agreement_ratio: float,
    contradiction: bool,
) -> dict:
    """
    Assign a confidence level to a claim cluster.

    Rules (applied in priority order):
      1. Contradiction present              → Low  (always overrides)
      2. Empty cluster or no directional    → Low  (agreement_ratio == 0.0)
         evidence (all-neutral claims)
      3. evidence_count >= 5 AND            → High
         agreement_ratio >= 0.75
      4. evidence_count >= 2                → Medium
      5. Anything else                      → Low

    Returns:
        {
            "confidence": "High" | "Medium" | "Low",
            "evidence_count": int,
            "agreement_ratio": float,
        }
    """
    evidence_count = len(cluster_claims)

    if contradiction:
        level: Literal["High", "Medium", "Low"] = "Low"
    elif evidence_count >= 5 and agreement_ratio >= 0.75:
        level = "High"
    elif evidence_count >= 2:
        level = "Medium"
    else:
        level = "Low"

    return {
        "confidence": level,
        "evidence_count": evidence_count,
        "agreement_ratio": round(agreement_ratio, 4),
    }
