import json
import re

_FALLBACK: dict = {"issue": "unknown", "explanation": "Reason unclear from reviews"}

_VAGUE_PATTERN = re.compile(
    r"mixed opinions|varied prefer|some (say|find|think)|others (say|find|think)|"
    r"different (opinions|views|experiences)|disagree|reviewers (have|express)",
    re.IGNORECASE,
)


def explain_contradiction(cluster_claims: list) -> dict:
    """
    Generate a short explanation of WHY reviewers disagree.
    Returns {"issue": "<label>", "explanation": "<1-2 sentences>"}.
    """
    if len(cluster_claims) < 2:
        return _FALLBACK

    lines = [
        f'- "{c["claim"]}" ({"positive" if c.get("polarity", 0) > 0 else "negative"})'
        for c in cluster_claims
        if c.get("claim", "").strip()
    ]

    if not lines:
        return _FALLBACK

    claims_block = "\n".join(lines)

    prompt = (
        "Analyze why these product review claims contradict each other.\n"
        "Rules:\n"
        "  1. Do NOT restate the claims. Do NOT say 'some say X while others say Y'.\n"
        "  2. Infer the most plausible CAUSE of the disagreement from the claim content.\n"
        "  3. Base your reasoning ONLY on the claims below — no external knowledge.\n"
        "  4. If no clear cause can be inferred, set explanation to 'Reason unclear from reviews'.\n"
        "  5. Keep explanation to 1-2 sentences maximum.\n\n"
        f"Claims:\n{claims_block}\n\n"
        "Return a JSON object with exactly two fields:\n"
        '  "issue": 1-3 word label for the disagreement topic (e.g. "weight", "build quality")\n'
        '  "explanation": causal explanation or "Reason unclear from reviews"\n\n'
        "Output valid JSON only. No extra text."
    )

    try:
        result = chat_completion(prompt)
        issue = str(result.get("issue", "")).strip()
        explanation = str(result.get("explanation", "")).strip()

        if not explanation or _VAGUE_PATTERN.search(explanation):
            explanation = "Reason unclear from reviews"

        # Truncate runaway explanations to 2 sentences
        sentences = re.split(r"(?<=[.!?])\s+", explanation)
        if len(sentences) > 2:
            explanation = " ".join(sentences[:2])

        return {
            "issue": issue or "unknown",
            "explanation": explanation,
        }
    except (ValueError, AttributeError, KeyError, TypeError):
        return _FALLBACK


# ---------------------------------------------------------------------------
# Updated contradiction detection snippet — drop this into your existing logic
# ---------------------------------------------------------------------------

def detect_contradictions(cluster_claims: list) -> dict:
    if not cluster_claims:
        return {"contradiction": False}

    polarities = {c.get("polarity") for c in cluster_claims}
    contradiction_detected = 1 in polarities and -1 in polarities

    result: dict = {"contradiction": contradiction_detected}

    if contradiction_detected:
        result["explanation"] = explain_contradiction(cluster_claims)

    return result
