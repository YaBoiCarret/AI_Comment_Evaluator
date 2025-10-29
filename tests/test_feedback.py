from ccqe.model import QualityScore
from ccqe.feedback import suggestion_from

def test_low_redundancy_message():
    qs = QualityScore(label="Low", score=0.2, signals={"length": 5, "intent_hits": 0, "redundancy": 0.6})
    msg = suggestion_from(qs)
    assert "Avoid repeating the code" in msg

def test_medium_needs_intent():
    qs = QualityScore(label="Medium", score=0.5, signals={"length": 6, "intent_hits": 0, "redundancy": 0.1})
    msg = suggestion_from(qs)
    assert "Add the reason or intent" in msg
