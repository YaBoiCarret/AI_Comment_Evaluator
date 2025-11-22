from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Set

from .preprocess import PreparedComment, tokenize_text


# Groups of words that represent the same conceptual signal.
# Mapping these to canonical tokens lets the model detect redundancy
# even when code and comments use slightly different wording.
SYNONYM_GROUPS: Dict[str, set[str]] = {
    "increment": {
        "increment", "inc", "increase", "add", "bump", "plus",
        "add_one", "increment_by_one",
    },
    "decrement": {
        "decrement", "dec", "decrease", "minus", "subtract",
        "subtract_one", "decrement_by_one",
    },
    "zero": {
        "zero", "equals_zero",
    },
    "one": {
        "one", "equals_one",
    },
    "check": {
        "check", "validate", "verify", "ensure", "assert", "guard",
    },
    "error": {
        "error", "fail", "failure", "bug", "issue", "problem", "exception",
    },
    "warn": {
        "warn", "warning", "caution",
    },
    "log": {
        "log", "record", "trace",
    },
    "config": {
        "config", "configuration", "setting", "settings", "option", "flag",
    },
    "remove": {
        "remove", "delete", "del", "erase", "clear", "cleanup", "drop",
    },
    "create": {
        "create", "make", "build", "construct", "init", "initialize", "setup",
    },
    "start": {
        "start", "begin", "launch",
    },
    "stop": {
        "stop", "halt", "exit", "abort", "break",
    },
    "loop": {
        "loop", "iterate", "iterate_over", "repeat",
    },
    "result": {
        "result", "output", "return_value", "value",
    },
    "input": {
        "input", "arg", "argument", "param", "parameter",
    },
}


def canonical_token(tok: str) -> str:
    """
    Map a token to a canonical concept if it appears in a synonym group.

    This allows different surface forms such as 'increment', 'add', and 'plus'
    to be treated as the same concept when computing redundancy.
    """
    t = tok.lower()
    for canon, group in SYNONYM_GROUPS.items():
        if t in group:
            return canon
    return t


def canonicalize_tokens(tokens: List[str]) -> List[str]:
    """Apply canonical_token to a sequence of tokens."""
    return [canonical_token(t) for t in tokens]


# Tokens that suggest the comment is explaining intent, rationale, or
# constraints rather than repeating implementation details.
INTENT_TOKENS: Set[str] = {
    "because", "so", "therefore", "hence", "why", "rationale",
    "tradeoff", "assume", "assumption", "intent", "reason", "explain",
    "due", "avoid", "ensure", "guarantee", "performance", "complexity",
}


@dataclass
class QualityScore:
    """
    Result of evaluating a single comment.

    label   : qualitative verdict ("High", "Medium", "Low")
    score   : numeric score in [0.0, 1.0]
    signals : raw features used by the model (length, intent_hits, redundancy)
    """
    label: str
    score: float
    signals: Dict[str, Any]


def jaccard(a: Set[str], b: Set[str]) -> float:
    """
    Compute Jaccard similarity between two token sets.

    Used as a redundancy measure to see how much the comment overlaps
    with the surrounding code after normalization and canonicalization.
    """
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b) or 1
    return inter / union


def predict_quality(pc: PreparedComment) -> QualityScore:
    """
    Score a PreparedComment and assign a High/Medium/Low quality label.

    The model combines three signals:
      - length: longer comments are more likely to carry useful context
      - intent_hits: presence of rationale-oriented words
      - redundancy: lexical/semantic overlap with the nearby code

    High redundancy lowers the score, while length and intent raise it.
    """
    # Comment tokens are already normalized by the preprocessing step.
    comment_tokens = pc.tokens

    # Code context has been normalized in preprocess; tokenize it here.
    code_tokens_raw = tokenize_text(pc.code_context)

    # Map both comment and code tokens into a shared concept space so that
    # synonyms (e.g., "increment" vs "add_one") contribute to redundancy.
    comment_tokens_canon = set(canonicalize_tokens(comment_tokens))
    code_tokens_canon = set(canonicalize_tokens(code_tokens_raw))

    # Intent detection is based on the original comment tokens.
    text_token_set = set(comment_tokens)
    intent_hits = len(text_token_set & INTENT_TOKENS)

    length = len(comment_tokens)
    redundancy = jaccard(comment_tokens_canon, code_tokens_canon)

    score = 0.0

    # Reward comments that are long enough to say something meaningful.
    if length >= 6:
        score += 0.35
    elif length >= 3:
        score += 0.20
    else:
        score += 0.05

    # Reward comments that mention intent, rationale, or constraints.
    if intent_hits >= 2:
        score += 0.35
    elif intent_hits == 1:
        score += 0.20

    # Penalize comments that closely mirror the code they sit next to.
    if redundancy > 0.5:
        score -= 0.30
    elif redundancy > 0.3:
        score -= 0.15

    # Clamp score into [0.0, 1.0] so labels have a stable scale.
    score = max(0.0, min(1.0, score))

    if score >= 0.7:
        label = "High"
    elif score >= 0.4:
        label = "Medium"
    else:
        label = "Low"

    return QualityScore(
        label=label,
        score=score,
        signals={
            "length": length,
            "intent_hits": intent_hits,
            "redundancy": round(redundancy, 2),
        },
    )
