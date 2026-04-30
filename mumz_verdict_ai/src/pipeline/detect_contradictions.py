"""Stage 4 — Flag clusters that contain contradictory claims."""

from typing import List

from schemas.claim_schema import Claim, ClusterSummary


def _is_contradictory(claims: List[Claim]) -> bool:
    """True when a cluster has both positive (+1) and negative (-1) claims."""
    polarities = {c.polarity for c in claims}
    return 1 in polarities and -1 in polarities


def explain_contradiction(claims: List[Claim]) -> str:
    pos_claims = [c for c in claims if c.polarity == 1]
    neg_claims = [c for c in claims if c.polarity == -1]

    if not pos_claims or not neg_claims:
        return "Reason unclear from reviews due to limited or inconsistent evidence."

    aspect = claims[0].aspect
    pos_count = len(pos_claims)
    neg_count = len(neg_claims)

    if pos_count > neg_count * 2 or neg_count > pos_count * 2:
        return (
            f"Most reviewers report {aspect} positively, while a smaller group reports negative experiences, "
            f"suggesting varied user expectations or conditions."
        )
    return f"Reviewers disagree on {aspect}, likely due to different expectations, usage contexts, or comparison standards."


def detect_contradictions(summaries: List[ClusterSummary]) -> List[ClusterSummary]:
    """
    Set has_contradiction=True and explanation on any ClusterSummary with polarity conflict.
    Mutates and returns the same list.
    """
    flagged = 0
    for s in summaries:
        if _is_contradictory(s.claims):
            s.has_contradiction = True
            s.explanation = explain_contradiction(s.claims)
            flagged += 1

    print(f"[contradictions] {flagged}/{len(summaries)} clusters flagged")
    return summaries
