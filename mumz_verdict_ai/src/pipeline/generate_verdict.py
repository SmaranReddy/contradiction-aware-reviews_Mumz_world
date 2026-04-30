"""Stage 5 — Aggregate cluster summaries into a final verdict."""

from typing import List, Literal

from schemas.claim_schema import Claim, ClusterSummary, FinalVerdict, VerdictItem
from pipeline.confidence_scoring import compute_confidence


def _representative_claim(claims: List[Claim]) -> str:
    """Pick the longest claim as the most descriptive representative."""
    return max(claims, key=lambda c: len(c.claim)).claim


def _aggregate_polarity(claims: List[Claim]) -> Literal[-1, 0, 1]:
    avg = sum(c.polarity for c in claims) / len(claims)
    if avg > 0.25:
        return 1
    if avg < -0.25:
        return -1
    return 0


def _overall_sentiment(items: List[VerdictItem]) -> Literal["Positive", "Mixed", "Negative"]:
    # Only count High/Medium confidence items to avoid noise
    reliable = [v for v in items if v.confidence != "Low"]
    pos = sum(1 for v in reliable if v.polarity == 1)
    neg = sum(1 for v in reliable if v.polarity == -1)
    if pos > neg * 1.5:
        return "Positive"
    if neg > pos * 1.5:
        return "Negative"
    return "Mixed"


def generate_verdict(
    summaries: List[ClusterSummary],
    product_name: str,
    total_reviews: int,
) -> FinalVerdict:
    """
    Convert cluster summaries into a ranked FinalVerdict.
    High-confidence, high-evidence items appear first.
    """
    items: List[VerdictItem] = []
    explanations: List[str] = []
    for s in summaries:
        conf = compute_confidence(s.claims, s.agreement_ratio, s.has_contradiction)
        items.append(
            VerdictItem(
                claim=_representative_claim(s.claims),
                aspect=s.aspect,
                evidence_count=conf["evidence_count"],
                confidence=conf["confidence"],
                contradiction_flag=s.has_contradiction,
                polarity=_aggregate_polarity(s.claims),
            )
        )
        if s.has_contradiction and s.explanation:
            explanations.append(s.explanation)

    # Drop singleton clusters (evidence_count=1, no contradiction) — they are
    # noise that skews the overall confidence distribution toward "Low".
    items = [v for v in items if v.evidence_count >= 2 or v.contradiction_flag]

    _rank = {"High": 0, "Medium": 1, "Low": 2}
    items.sort(key=lambda x: (_rank[x.confidence], -x.evidence_count))

    explanation = " ".join(explanations) if explanations else "No contradictions detected among reviewers."

    return FinalVerdict(
        product_name=product_name,
        total_reviews=total_reviews,
        verdict_items=items,
        overall_sentiment=_overall_sentiment(items),
        explanation=explanation,
    )
