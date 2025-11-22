from ccqe.model import predict_quality
from ccqe.preprocess import PreparedComment


class DummySpan:
    file = None
    lineno = 1
    text = ""
    context = "inline"
    func = None
    cls = None


def test_predict_quality_handles_empty_tokens():
    # No comment tokens and empty code context jaccard
    span = DummySpan()
    prepared = PreparedComment(span=span, tokens=[], code_context="")
    q = predict_quality(prepared)

    # Ensure we still get a valid QualityScore
    assert q.label in {"High", "Medium", "Low"}
    assert 0.0 <= q.score <= 1.0
