
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from .preprocess import PreparedComment, tokenize_text

INTENT_TOKENS = {
    "because","so","so that","therefore","hence","why","rationale","tradeoff","assume","assumption",
    "intent","reason","explain","due","avoid","ensure","guarantee","performance","complexity"
}

@dataclass
class QualityScore:
    label: str
    score: float
    signals: Dict[str, Any]

def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b) or 1
    return inter / union

def predict_quality(pc: PreparedComment) -> QualityScore:
    text_tokens = set(pc.tokens)
    code_tokens = set(tokenize_text(pc.code_context))

    intent_hits = len(text_tokens & INTENT_TOKENS)
    length = len(pc.tokens)
    redundancy = jaccard(text_tokens, code_tokens)

    score = 0.0
    if length >= 6:
        score += 0.35
    elif length >= 3:
        score += 0.20
    else:
        score += 0.05

    if intent_hits >= 2:
        score += 0.35
    elif intent_hits == 1:
        score += 0.20

    if redundancy > 0.5:
        score -= 0.30
    elif redundancy > 0.3:
        score -= 0.15

    score = max(0.0, min(1.0, score))
    if score >= 0.7:
        label = "High"
    elif score >= 0.4:
        label = "Medium"
    else:
        label = "Low"

    return QualityScore(label=label, score=score, signals={
        "length": length,
        "intent_hits": intent_hits,
        "redundancy": round(redundancy, 2)
    })
