from ccqe.model import QualityScore
from ccqe.feedback import suggestion_from


def test_feedback_for_high_quality_comment():
    score = QualityScore(
        label="High",
        score=0.9,
        signals={"length": 12, "intent_hits": 2, "redundancy": 0.0},
    )
    msg = suggestion_from(score).lower()
    assert "keep this comment" in msg or "looks good" in msg


def test_feedback_for_very_short_low_comment():
    score = QualityScore(
        label="Low",
        score=0.1,
        signals={"length": 1, "intent_hits": 0, "redundancy": 0.1},
    )
    msg = suggestion_from(score).lower()
    assert "expand the comment" in msg or "too short" in msg