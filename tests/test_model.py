
from ccqe.preprocess import PreparedComment
from ccqe.model import predict_quality

class DummySpan:
    def __init__(self, lineno=1, text="", file="x.py"):
        self.file = file
        self.lineno = lineno
        self.text = text
        self.context = "inline"
        self.func = None
        self.cls = None

def pc(text, code="def f():\n    return 1"):
    return PreparedComment(DummySpan(text=text), text.lower().split(), code)

def test_high_quality_with_intent():
    p = pc("ensure stability because disk access is slow so that results are consistent")
    q = predict_quality(p)
    assert q.label in ("High", "Medium")
    assert q.score >= 0.4

def test_low_quality_redundant():
    p = pc("return i plus one", "def add_one(i):\n    return i + 1")
    q = predict_quality(p)
    assert q.label in ("Low", "Medium")

def test_medium_suggestion():
    p = pc("handle error case quickly", "if b == 0:\n    return 0")
    q = predict_quality(p)
    assert 0.2 <= q.score <= 0.8
