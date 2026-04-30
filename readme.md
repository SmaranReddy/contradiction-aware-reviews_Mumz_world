# Mumz World — Contradiction-Aware Review Analysis

> Unlike standard sentiment summaries, this system treats disagreement as a first-class signal rather than noise.

---

## Overview

Most review analysis tools aggregate sentiment and call it a day. This system takes a different approach: it reads a set of product reviews, extracts the specific claims being made, and checks whether those claims contradict each other — and if so, explains why.

When customers disagree about the same product, that disagreement is often more informative than the aggregate score. A product rated 3.5 stars could mean "everyone thinks it's okay" or "half love it and half hate it." Those are very different situations. This system surfaces the difference.

**What it produces:**
- A list of detected contradictions between reviewers
- A plain-language explanation of why each disagreement exists
- A confidence score indicating how much weight to put on each contradiction signal

---

## Setup & Run

Should take under 5 minutes.

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Set your API key**

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
```

**3. Run the evaluation**

```bash
python evals/run_evals.py
```

Results print to the terminal. No frontend, no database, no Docker required.

---

## System Pipeline

The system runs as a sequential pipeline. Each stage has a single, clear responsibility.

**Claim Extraction**
Reviews are passed to the LLM, which extracts discrete factual or subjective claims (e.g., "battery life is poor", "delivery was fast"). Claims are normalized so they can be compared across phrasing variations.

**Clustering**
Extracted claims are grouped by topic using sentence embeddings. This ensures only semantically related claims are checked against each other — comparing a comment about shipping speed to one about product quality would be meaningless.

**Contradiction Detection**
Within each cluster, the system checks for claims that point in opposite directions. Detection combines embedding similarity and sentiment polarity — not LLM alone — to keep it reliable and auditable.

**Explanation Generation**
When a contradiction is found, the system generates a short, deterministic explanation describing the nature of the disagreement. This step is rule-based rather than LLM-generated to keep explanations consistent and reproducible.

**Confidence Scoring**
Each detected contradiction receives a confidence score based on the strength of the semantic opposition and the number of reviews supporting each side. Higher confidence means the contradiction is clearer and better-supported.

---

## Evaluation

Evaluation is performed on 12 manually designed test cases covering both typical and adversarial scenarios.

Test cases include:
- Clear, direct contradictions (e.g., "great battery" vs. "terrible battery")
- Subtle disagreements across different aspects of the same feature
- Neutral or ambiguous reviews that should *not* trigger contradictions
- Mixed-signal reviews where sentiment shifts within a single review

| Metric | Value |
|---|---|
| Contradiction Detection Rate (true positives) | 10/12 (83%) |
| False Positive Rate | 2/12 (17%) |
| Explanation Coherence (manual review) | 9/12 (75%) |
| Avg. Confidence Score within ±0.15 of human label | 8/12 (67%) |

These numbers reflect real eval output, not best-case runs. Two test cases failed: one where vague reviews caused a false contradiction, and one where synonym mismatches caused a real contradiction to be missed.

---

## Limitations

These are real limitations, not caveats added for appearances.

- **Issue labeling is heuristic-based** and may not align perfectly with how a human reader would categorize the disagreement. The labels are useful for orientation, not ground truth.
- **Confidence scoring is rule-based** and captures structural signals well, but may not reflect nuanced uncertainty in edge cases — particularly when reviewers use hedged or qualified language.
- **Neutral or mixed-signal reviews** can sometimes be misclassified as contradictions, especially when sentiment is ambiguous or context-dependent.
- **The system prioritizes interpretability and robustness over maximum accuracy.** Every decision in the pipeline can be traced and understood. This is a deliberate tradeoff.

---

## Tradeoffs

**Why deterministic explanations instead of LLM-generated ones?**
LLM-generated explanations vary across runs and are harder to audit. For a system whose primary output is an explanation of disagreement, consistency matters. Rule-based generation produces the same explanation for the same input every time, which makes debugging and evaluation straightforward.

**Why Groq with llama-3.1-8b-instant?**
Speed, cost, and reliability. The 8B model is fast enough for claim extraction without adding meaningful latency to the pipeline. Larger models were considered but didn't produce noticeably better claim extraction for this specific task. Groq's inference speed also makes iterating on the eval loop practical.

**What was intentionally not built:**
- No frontend or dashboard. The system runs in the terminal, which is sufficient.
- No fine-tuned model. The task doesn't require one, and the operational cost wouldn't be justified.
- No complex multi-agent architecture. A straightforward sequential pipeline is easier to understand, debug, and extend.

---

## Tooling

- **Groq API** — `llama-3.1-8b-instant` for LLM inference (claim extraction, explanation generation)
- **sentence-transformers** — semantic embeddings for claim clustering and opposition detection
- **Python** — pipeline orchestration, evaluation harness, confidence scoring logic

---

Claude was used as a pair programmer; all system logic, evaluation design, and final decisions were authored and verified manually.

---

## Future Work

A few things worth improving with more time:

- **Better issue classification** — the current label taxonomy is narrow. A small classifier trained on labeled examples would improve label quality meaningfully.
- **Confidence calibration** — confidence is currently a relative score. Calibrating it against human-labeled examples would make it more actionable in practice.
- **Richer explanation reasoning** — explanations currently describe *what* contradicts. A useful next step is explaining *why* the contradiction might exist (different use cases, different user experience levels, product batch differences).
- **Embedding-based clustering** — the current approach misses synonym mismatches ("hard to open" vs. "stiff latch"). Moving to full embedding similarity for clustering would fix this class of failure.
