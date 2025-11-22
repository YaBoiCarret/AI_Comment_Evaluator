from __future__ import annotations

from .model import QualityScore


def suggestion_from(score: QualityScore) -> str:
    """
    Derive a short, human-readable suggestion from a QualityScore.

    The goal is to explain how the comment could be improved (or why it is
    already good) based on the label and the underlying signals. This keeps
    the feedback aligned with the model's reasoning rather than returning a
    bare High/Medium/Low classification.
    """
    s = score.signals

    # High-quality comments already explain purpose, reasoning, or assumptions.
    # Encourage the developer to keep them as they are.
    if score.label == "High":
        return (
            "Keep this comment. It explains purpose or reasoning and adds "
            "context beyond the code."
        )

    # Medium-quality comments are on the right track but often lack either
    # a clear reason/intent or one extra detail about constraints/tradeoffs.
    if score.label == "Medium":
        if s["intent_hits"] == 0:
            return (
                "Add the reason or intent. Explain why the code exists and "
                "note key assumptions."
            )
        return (
            "Add one clarifying detail such as a constraint or tradeoff to "
            "strengthen the comment."
        )

    # Low-quality comments fall through to here. Use signals to decide
    # why they are weak and tailor the suggestion accordingly.

    # Highly redundant comments just restate the code. Ask for intent,
    # assumptions, or side effects instead of paraphrasing the implementation.
    if s["redundancy"] >= 0.5:
        return (
            "Avoid repeating the code in words. Focus on intent, assumptions, "
            "or side effects."
        )

    # Very short comments lack enough information to be helpful. Ask the
    # developer to expand them to cover purpose and impact of changes.
    if s["length"] < 3:
        return (
            "Expand the comment to explain purpose and what would break if "
            "changed."
        )

    # Generic fallback for remaining low-quality cases: ask for clearer intent
    # and non-obvious constraints.
    return (
        "Clarify intent and assumptions. Add what, why, and any non-obvious "
        "constraints."
    )
