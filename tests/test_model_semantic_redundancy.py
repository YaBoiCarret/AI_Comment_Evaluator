# tests/test_model_semantic_redundancy.py

from ccqe.model import predict_quality
from ccqe.preprocess import PreparedComment, tokenize_text, normalize_code_text


class DummySpan:
    """Minimal stand-in for CommentSpan for testing."""
    def __init__(self, text: str) -> None:
        self.file = None
        self.lineno = 1
        self.text = text
        self.context = "inline"
        self.func = None
        self.cls = None


def test_semantic_redundancy_for_increment_zero():
    # Comment describes the same behavior as the code, but in words
    comment_text = "increment i if zero"

    # Code that implements exactly that
    code = "if i == 0:\n    i += 1\n"

    span = DummySpan(comment_text)

    # Build a PreparedComment similar to what the real pipeline does:
    # - tokenize the comment text
    # - normalize the code context (numbers + operations)
    tokens = tokenize_text(span.text)
    code_context = normalize_code_text(code)

    prepared = PreparedComment(
        span=span,
        tokens=tokens,
        code_context=code_context,
    )

    quality = predict_quality(prepared)

    # Redundancy should be clearly non-trivial: the model should see these
    # as talking about the same concept, even though strings differ.
    redundancy = quality.signals["redundancy"]
    assert redundancy >= 0.5, f"Expected high redundancy, got {redundancy}"

    # We still expect a valid label and score in [0, 1]
    assert quality.label in {"High", "Medium", "Low"}
    assert 0.0 <= quality.score <= 1.0
