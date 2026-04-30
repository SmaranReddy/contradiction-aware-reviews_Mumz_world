"""
Moms Verdict AI — Pipeline Entry Point

Usage:
    python src/main.py
    python src/main.py --reviews data/reviews_sample.json --output output/verdict.json --product "Baby Stroller XL"
"""

from dotenv import load_dotenv
load_dotenv()

import argparse
import json
import os
import sys
from pathlib import Path

print("GEMINI KEY LOADED:", bool(os.getenv("GEMINI_API_KEY")))

# Make src/ importable as the root package path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.filter_reviews import filter_reviews, load_reviews
from pipeline.extract_claims import extract_all_claims
from pipeline.cluster_claims import cluster_claims, summarize_clusters
from pipeline.detect_contradictions import detect_contradictions
from pipeline.generate_verdict import generate_verdict
from pipeline.hallucination_checker import run_hallucination_check


def run_pipeline(
    reviews_path: str,
    output_path: str,
    product_name: str,
) -> dict:
    sep = "=" * 60
    print(f"\n{sep}\nMoms Verdict AI — Pipeline Start\n{sep}")

    # Stage 1: Load + filter
    raw = load_reviews(reviews_path)
    reviews = filter_reviews(raw)

    # Stage 2: Extract claims
    claims = extract_all_claims(reviews)
    if not claims:
        raise RuntimeError("No claims extracted. Check your API key and reviews file.")

    # Stage 3: Cluster
    clusters = cluster_claims(claims)
    summaries = summarize_clusters(clusters)

    # Stage 4: Detect contradictions
    summaries = detect_contradictions(summaries)

    # Stage 5: Generate verdict
    verdict = generate_verdict(summaries, product_name=product_name, total_reviews=len(reviews))

    # Stage 6: Hallucination check
    verdict = run_hallucination_check(verdict, reviews)

    # Persist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    output = verdict.model_dump()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\n{sep}")
    print(f"Verdict saved  → {output_path}")
    print(f"Sentiment      : {verdict.overall_sentiment}")
    print(f"Verdict items  : {len(verdict.verdict_items)}")
    print(f"Hallucinations : {len(verdict.hallucination_flags)}")
    print(f"{sep}\n")
    return output


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Moms Verdict AI Pipeline")
    p.add_argument("--reviews", default="data/reviews_sample.json")
    p.add_argument("--output", default="output/verdict.json")
    p.add_argument("--product", default=os.environ.get("PRODUCT_NAME", "Unknown Product"))
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_pipeline(args.reviews, args.output, args.product)
