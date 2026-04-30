 # Contradiction-Aware Moms Verdict AI        
                                                                                          
  ## Summary
                                                                                                                                                                                                         
  Contradiction-Aware Moms Verdict AI is a structured review analysis system that takes product reviews, extracts factual claims, detects where reviewers directly contradict each other, and explains
  why they disagree — returning a confidence score grounded in evidence. It is built for mothers on Mumzworld who need reliable product intelligence before purchasing items for their children. Star    
  ratings obscure the most important signal: specific disagreements between real users. This system surfaces that signal clearly and honestly.

  > Unlike standard sentiment summaries, this system treats disagreement as first-class signal rather than noise.

  ---

  ## Why This Problem

  Mumzworld's core users are mothers making decisions about products that affect their children. A stroller that "folds easily" in 40 reviews and "impossible to fold" in 12 reviews is not a 4.2-star
  product — it's a product with a real usability split that a star average buries. Averaging sentiment loses the signal that matters most: **who disagrees, about what, and why**.

  Contradiction detection surfaces that signal. It tells a mom: *"Most reviewers love the storage, but parents of newborns consistently report the recline doesn't go flat enough."* That's actionable. A
   star rating is not.

  Disagreement is not noise — it is the most valuable signal in decision-making.

  ---

  ## Why AI

  Rule-based systems can flag when positive and negative words co-exist in a review set, but they cannot determine whether two reviews are actually contradicting the same claim. "Hard to open" and
  "stiff latch" are the same complaint — a keyword rule treats them as unrelated. Semantic understanding is required to cluster claims accurately across varied phrasing.

  Explanation generation cannot be templated. The reason reviewers disagree varies — it may be a use-case split (travel vs. daily use), a user-experience gap (first-time parents vs. experienced ones),
  or a product batch change. Generating a coherent, grounded explanation from a set of conflicting quotes requires language understanding, not pattern matching.

  The parts of this system that do not require AI are kept deterministic by design: confidence scoring uses a fixed formula, contradiction thresholds are numeric, and hallucination checks are
  rule-based verification against source quotes. AI is used where semantics are unavoidable; arithmetic is used where arithmetic is sufficient.

  ---

  ## System Overview

  Raw Reviews
      │
      ▼
  [1] Filter          — Remove reviews under 20 chars, non-English, duplicates
      │
      ▼
  [2] Claim Extraction — LLM extracts structured claims: {aspect, polarity, quote}
      │
      ▼
  [3] Clustering       — Group claims by aspect (e.g. "assembly", "durability")
      │
      ▼
  [4] Contradiction Detection — Per-cluster: flag aspect if both positive + negative claims exist above threshold
      │
      ▼
  [5] Explanation      — LLM explains the disagreement using actual quotes as evidence
      │
      ▼
  [6] Confidence Score — Deterministic: f(review count, agreement ratio, recency weight)
      │
      ▼
  [7] Hallucination Check — Verify explanation claims are grounded in source quotes
      │
      ▼
  Structured JSON Output

  ---

  ## Key Features

  **Contradiction Detection**
  Flags aspects where a statistically meaningful split exists between positive and negative claims. Not just "mixed reviews" — specific: *assembly is contradicted, durability is not*.

  **Disagreement Explanation**
  The system explains *why* reviewers split, using their own words. It separates user-type patterns (new parents vs. experienced), use-case patterns (travel vs. daily use), and version/batch
  differences where detectable.

  **Deterministic Confidence Scoring**
  Confidence is computed as a formula, not asked from an LLM:
  confidence = (agreement_ratio × 0.5) + (review_count_score × 0.3) + (recency_score × 0.2)
  This makes scores reproducible and auditable. An LLM cannot explain why it gave something 0.73 confidence — this can.

  **Hallucination Detection**
  After generating explanations, a verification pass checks that every factual claim in the output is grounded in an actual review quote. Ungrounded claims are flagged or removed before final output.

  **Evidence Snippets**
  Every conclusion is accompanied by the specific review quotes that produced it. The output is traceable.

  ---

  ## Example Output

  ```json
  {
    "product_id": "stroller-x200",
    "total_reviews_analyzed": 47,
    "verdict": "Mostly positive with a significant contradiction on ease of folding.",
    "contradictions": [
      {
        "aspect": "folding mechanism",
        "contradicted": true,
        "positive_count": 31,
        "negative_count": 14,
        "confidence": 0.71,
        "explanation": "Most reviewers find the fold intuitive after a few uses. Negative reports cluster around first-time use and come disproportionately from reviewers who note they 'read no
  manual'. One reviewer flagged a design change in late 2024 batches.",
        "supporting_quotes": [
          "Folds in one hand once you get the hang of it — took me 2 tries.",
          "I cannot for the life of me figure out how to collapse this thing."
        ],
        "hallucination_check": "passed"
      }
    ],
    "non_contradicted_aspects": [
      {
        "aspect": "storage capacity",
        "sentiment": "positive",
        "confidence": 0.89,
        "summary": "Consistent praise across reviewer types."
      }
    ],
    "low_confidence_aspects": [],
    "warnings": []
  }

  ---
  Evaluation

  Evaluation is performed on 12 manually designed test cases covering both typical and adversarial scenarios.

  Cases include: clean contradiction, no contradiction (false positive check), single review, sparse data (2 reviews), all-negative, all-positive, vague reviews, synonym mismatch ("hard to open" vs
  "stiff latch"), multilingual edge case, fabricated claim injection, high-volume agreement, and mixed-product reviews.

  ┌──────────────────────────────────────────────────┬─────────────┐
  │                      Metric                      │   Result    │
  ├──────────────────────────────────────────────────┼─────────────┤
  │ Contradiction detection accuracy                 │ 10/12 (83%) │
  ├──────────────────────────────────────────────────┼─────────────┤
  │ Issue identification accuracy                    │ 9/12 (75%)  │
  ├──────────────────────────────────────────────────┼─────────────┤
  │ Confidence score within ±0.15 of human label     │ 8/12 (67%)  │
  ├──────────────────────────────────────────────────┼─────────────┤
  │ Hallucination rate (ungrounded claims in output) │ 1/12 (8%)   │
  └──────────────────────────────────────────────────┴─────────────┘

  Known failures:
  - Case 7 (vague reviews): System returned a contradiction where none existed — reviews were vague enough that the LLM extracted opposing claims from ambiguous phrasing.
  - Case 11 (synonym mismatch): "hard to open" and "stiff latch" were not clustered together, so the contradiction was missed. Would require embedding-based clustering to fix.

  ---
  Failure Modes

  Vague reviews ("great product, love it") produce no extractable claims. The system handles this gracefully — these reviews contribute to count but not to aspect analysis. When too many reviews are
  vague, confidence drops and a warning is emitted.

  Sparse data (fewer than 5 reviews per aspect) produces low-confidence scores. The system does not suppress output but flags it clearly. Two reviews saying opposite things is not a meaningful
  contradiction.

  Synonym mismatches are the biggest structural limitation. The current clustering is keyword + LLM-assisted, not embedding-based. "Difficult to assemble" and "hard to put together" may not cluster
  together reliably. When this happens, the system misses a real contradiction.

  "Reason unclear" appears in the explanation field when the LLM cannot find a coherent pattern distinguishing positive from negative reviewers. This is intentional — it is better to say the reason is
  unclear than to hallucinate a pattern.

  ---
  Tradeoffs

  No RAG — There is no retrieval layer. All analysis happens over the reviews passed in. RAG would help with product background (e.g., known batch issues) but adds infra complexity that is outside a
  5-hour scope. The system notes when a pattern might be a batch issue but does not assert it.

  Simple clustering — Keyword + LLM aspect tagging instead of embedding similarity. Faster, cheaper, more debuggable. The tradeoff is synonym mismatches (documented above). Moving to sentence
  embeddings is the obvious next step.

  Deterministic confidence — A formula rather than an LLM-assigned score. This trades some nuance for reproducibility and explainability. The formula weights are heuristic, not learned.

  Cut for time:
  - Batch product comparison (compare two products across same aspects)
  - Reviewer segmentation by verified purchase / age group
  - UI layer
  - Async processing for large review volumes

  ---
  Multilingual Consideration

  Mumzworld operates across English and Arabic markets, with a significant portion of its user base writing reviews in Arabic. This prototype focuses exclusively on English — the filtering step
  discards non-English reviews rather than attempting to process them.

  Extending to Arabic is straightforward in principle: the LLM-based claim extraction and explanation steps are language-agnostic given a multilingual model. The practical work involves validating that
   aspect clustering performs equally well on Arabic text, handling right-to-left formatting in output, and ensuring the hallucination check correctly matches Arabic quotes back to source reviews. The
  deterministic confidence formula requires no changes for Arabic support.

  ---
  Demo (Loom)

  [Insert Loom link]

  Walkthrough covers five scenarios:

  - Normal case — product with clear majority sentiment, no contradictions flagged
  - Contradiction case — aspect-level split detected, explanation generated with supporting quotes
  - Sparse data — 3-review product, low-confidence output with appropriate warnings
  - Noisy reviews — vague and off-topic reviews filtered out, pipeline continues on valid claims
  - Uncertainty handling — system outputs "Reason unclear" rather than fabricating an explanation

  ---
  Tooling

  ┌────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────┐
  │            Tool            │                                      Role                                       │
  ├────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────┤
  │ Claude (claude-sonnet-4-6) │ Prompt design, iteration, debugging extraction failures, reviewing eval results │
  ├────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────┤
  │ OpenRouter                 │ LLM inference endpoint — model-agnostic routing with fallback support           │
  ├────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────┤
  │ Python + dataclasses       │ Core pipeline logic                                                             │
  ├────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────┤
  │ pytest                     │ Eval runner                                                                     │
  └────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────┘

  How Claude was used: Pair-coding the extraction prompt (went through ~6 iterations before aspect clustering was stable), debugging why contradiction detection was firing on non-contradictions, and
  stress-testing the hallucination check logic.

  What didn't work: Initial prompt asked the LLM to detect contradictions directly from raw reviews — it hallucinated patterns frequently. Separating claim extraction from contradiction detection
  (structured intermediate step) fixed this.

  ---
  Setup

  Setup completes in under 5 minutes with no external infrastructure required.

  pip install -r requirements.txt

  # Add your OpenRouter API key
  export OPENROUTER_API_KEY=your_key_here

  # Run on a product
  python main.py --product_id stroller-x200 --reviews_file data/reviews.json

  # Run evaluation suite
  python eval/run_evals.py

  Requires Python 3.10+. No database, no Docker, no other dependencies.

  ---
  Time Log

  - 0:00–1:00 — Problem scoping, pipeline design, prompt v1
  - 1:00–2:00 — Claim extraction + clustering (most debugging here)
  - 2:00–3:00 — Contradiction detection logic + confidence formula
  - 3:00–4:00 — Hallucination check + explanation generation
  - 4:00–5:00 — Eval suite, test cases, README

  ---
  AI Usage Note

  Used Claude (claude-sonnet-4-6 via Claude Code) throughout — primarily for prompt iteration, debugging extraction failures, and reviewing eval output for edge cases. LLM inference in the pipeline
  runs via OpenRouter. Claude was used as a pair programmer; all system logic, evaluation criteria, and final decisions were authored and verified manually.
  ```
