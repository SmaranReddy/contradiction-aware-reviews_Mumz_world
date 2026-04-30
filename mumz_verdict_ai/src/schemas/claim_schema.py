from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel, Field


class Claim(BaseModel):
    claim: str
    aspect: str  # quality, value, durability, safety, ease_of_use, design, size, shipping, other
    polarity: Literal[-1, 0, 1]
    review_id: str


class ClusterSummary(BaseModel):
    cluster_id: int
    aspect: str
    claims: List[Claim]
    has_contradiction: bool = False
    agreement_ratio: float = 0.0
    explanation: str = ""


class VerdictItem(BaseModel):
    claim: str
    aspect: str
    evidence_count: int
    confidence: Literal["High", "Medium", "Low"]
    contradiction_flag: bool
    polarity: Literal[-1, 0, 1]


class FinalVerdict(BaseModel):
    product_name: str
    total_reviews: int
    verdict_items: List[VerdictItem]
    overall_sentiment: Literal["Positive", "Mixed", "Negative"]
    hallucination_flags: List[str] = Field(default_factory=list)
    explanation: str = ""
