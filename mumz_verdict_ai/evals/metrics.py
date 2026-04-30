"""Eval metrics for the Moms Verdict AI test suite."""

from typing import List


def contradiction_accuracy(results: list) -> float:
    valid = [r for r in results if "error" not in r]
    if not valid:
        return 0.0
    return sum(r["contradiction_match"] for r in valid) / len(valid)


def issue_accuracy(results: list) -> float:
    """Only counts test cases where expected.issue is explicitly set."""
    relevant = [
        r for r in results
        if "error" not in r and r.get("expected", {}).get("issue") is not None
    ]
    if not relevant:
        return 0.0
    return sum(r["issue_match"] for r in relevant) / len(relevant)


def confidence_accuracy(results: list) -> float:
    """Only counts test cases where expected.confidence is explicitly set."""
    relevant = [
        r for r in results
        if "error" not in r and r.get("expected", {}).get("confidence") is not None
    ]
    if not relevant:
        return 0.0
    return sum(r["confidence_match"] for r in relevant) / len(relevant)


def hallucination_rate(claims: List[str], reviews: List[str]) -> float:
    if not claims:
        return 0.0
    review_blob = " ".join(reviews).lower()
    hallucinated = 0
    for claim in claims:
        words = [w for w in claim.lower().split() if len(w) > 3]
        if not words:
            continue
        matched = sum(1 for w in words if w in review_blob)
        if matched / len(words) < 0.4:
            hallucinated += 1
    return hallucinated / len(claims)


def normalize_issue(issue: str) -> str:
    mapping = {
        "ease_of_use": "comfort",
        "size": "weight",
    }
    return mapping.get(issue, issue)


def explanation_quality(output: dict) -> bool:
    explanation = output.get("explanation", "")
    if "reason unclear" in explanation.lower():
        return True
    if len(explanation.split()) < 5:
        return False
    return True
