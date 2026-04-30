"""Stage 4 — Flag clusters that contain contradictory claims."""

from typing import List

from schemas.claim_schema import Claim, ClusterSummary


def _is_contradictory(claims: List[Claim]) -> bool:
    """True when a cluster has both positive (+1) and negative (-1) claims."""
    polarities = {c.polarity for c in claims}
    return 1 in polarities and -1 in polarities


def detect_contradictions(summaries: List[ClusterSummary]) -> List[ClusterSummary]:
    """
    Set has_contradiction=True on any ClusterSummary with polarity conflict.
    Mutates and returns the same list.
    """
    flagged = 0
    for s in summaries:
        if _is_contradictory(s.claims):
            s.has_contradiction = True
            flagged += 1

    print(f"[contradictions] {flagged}/{len(summaries)} clusters flagged")
    return summaries
