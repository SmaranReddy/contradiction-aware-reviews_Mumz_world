"""
Test-case-based eval runner for the Moms Verdict AI pipeline.

Usage:
    python evals/run_evals.py
"""

import json
import sys
from pathlib import Path

_root = Path(__file__).parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root))

from pipeline.filter_reviews import filter_reviews
from pipeline.extract_claims import extract_all_claims
from pipeline.cluster_claims import cluster_claims, summarize_clusters
from pipeline.detect_contradictions import detect_contradictions
from pipeline.generate_verdict import generate_verdict
from pipeline.hallucination_checker import run_hallucination_check
from evals.metrics import (
    contradiction_accuracy,
    issue_accuracy,
    confidence_accuracy,
    hallucination_rate,
    explanation_quality,
    normalize_issue,
)


def run_pipeline(reviews: list) -> dict:
    """Run the full pipeline on a list of plain review strings."""
    raw = [{"id": str(i), "text": r} for i, r in enumerate(reviews)]
    filtered = filter_reviews(raw)
    claims = extract_all_claims(filtered)
    if not claims:
        return {"verdict_items": [], "overall_sentiment": "Mixed", "hallucination_flags": []}
    clusters = cluster_claims(claims)
    summaries = summarize_clusters(clusters)
    summaries = detect_contradictions(summaries)
    verdict = generate_verdict(summaries, product_name="eval", total_reviews=len(filtered))
    verdict = run_hallucination_check(verdict, filtered)
    return verdict.model_dump()


def _map_output(verdict: dict) -> dict:
    """Reduce a full FinalVerdict dict to the fields the eval compares."""
    items = verdict.get("verdict_items", [])

    contradiction = any(i["contradiction_flag"] for i in items)

    aspect_counts: dict = {}
    conf_counts: dict = {}
    for item in items:
        aspect_counts[item["aspect"]] = aspect_counts.get(item["aspect"], 0) + 1
        conf_counts[item["confidence"]] = conf_counts.get(item["confidence"], 0) + 1

    issue = max(aspect_counts, key=aspect_counts.get) if aspect_counts else None
    confidence = max(conf_counts, key=conf_counts.get) if conf_counts else "Low"
    claims = [item["claim"] for item in items]
    explanation = verdict.get("explanation", "")

    return {"contradiction": contradiction, "issue": issue, "confidence": confidence, "claims": claims, "explanation": explanation}


def run_evals() -> dict:
    test_cases_path = _root / "data" / "eval" / "test_cases.json"
    with open(test_cases_path, encoding="utf-8") as f:
        test_cases = json.load(f)

    results = []
    for tc in test_cases:
        print(f"\n[eval] {tc['id']}")
        try:
            verdict = run_pipeline(tc["reviews"])
            output = _map_output(verdict)
            hal = hallucination_rate(output["claims"], tc["reviews"])

            exp = tc["expected"]
            result = {
                "id": tc["id"],
                "expected": exp,
                "output": {k: v for k, v in output.items() if k != "claims"},
                "hallucination_rate": hal,
                "contradiction_match": output["contradiction"] == exp["contradiction"],
                "issue_match": exp.get("issue") is None or normalize_issue(output["issue"] or "") == exp.get("issue"),
                "confidence_match": exp.get("confidence") is None or output["confidence"] == exp.get("confidence"),
                "explanation_valid": explanation_quality(output),
            }
        except Exception as e:
            print(f"  ERROR: {e}")
            result = {
                "id": tc["id"],
                "expected": tc["expected"],
                "error": str(e),
                "hallucination_rate": 0.0,
                "contradiction_match": False,
                "issue_match": False,
                "confidence_match": False,
                "explanation_valid": False,
            }

        results.append(result)
        c_status = "PASS" if result["contradiction_match"] else "FAIL"
        print(f"  contradiction [{c_status}]  explanation_valid={result['explanation_valid']}  hal={result['hallucination_rate']:.1%}")

    metrics = {
        "contradiction_accuracy": contradiction_accuracy(results),
        "issue_accuracy": issue_accuracy(results),
        "confidence_accuracy": confidence_accuracy(results),
        "hallucination_rate": sum(r["hallucination_rate"] for r in results) / len(results),
    }

    bar = "=" * 50
    print(f"\n{bar}\nEVAL METRICS\n{bar}")
    print(f"  contradiction_accuracy : {metrics['contradiction_accuracy']:.1%}")
    print(f"  issue_accuracy         : {metrics['issue_accuracy']:.1%}")
    print(f"  confidence_accuracy    : {metrics['confidence_accuracy']:.1%}")
    print(f"  hallucination_rate     : {metrics['hallucination_rate']:.1%}")
    print(bar)

    failed = [
        r["id"] for r in results
        if not r["contradiction_match"]
        or not r["issue_match"]
        or not r["confidence_match"]
        or not r["explanation_valid"]
    ]
    if failed:
        print("\nFAILED CASES:")
        for fid in failed:
            print(f"  {fid}")

    return metrics


if __name__ == "__main__":
    run_evals()
