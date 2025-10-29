from pathlib import Path
from ccqe.parser import extract_python_entities

def test_extracts_inline_and_docstrings(tmp_path: Path):
    code = '''\
"""Module docstring about intent and assumptions."""
# top inline
def f(x):
    """Explain why we clamp x to avoid overflow."""
    # add one
    return x + 1
'''
    p = tmp_path / "ex.py"
    p.write_text(code, encoding="utf-8")
    spans, src = extract_python_entities(p)
    texts = [s.text for s in spans]
    assert any("Module docstring" in t for t in texts)
    assert any("top inline" in t for t in texts)
    assert any("clamp x" in t for t in texts)
