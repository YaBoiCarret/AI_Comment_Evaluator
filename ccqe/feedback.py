
from __future__ import annotations
from .model import QualityScore

def suggestion_from(score: QualityScore) -> str:
    s = score.signals
    if score.label == "High":
        return "Keep this comment. It explains purpose or reasoning and adds context beyond the code."
    if score.label == "Medium":
        if s["intent_hits"] == 0:
            return "Add the reason or intent. Explain why the code exists and note key assumptions."
        return "Add one clarifying detail such as a constraint or tradeoff to strengthen the comment."
    if s["redundancy"] >= 0.5:
        return "Avoid repeating the code in words. Focus on intent, assumptions, or side effects."
    if s["length"] < 3:
        return "Expand the comment to explain purpose and what would break if changed."
    return "Clarify intent and assumptions. Add what, why, and any non-obvious constraints."
