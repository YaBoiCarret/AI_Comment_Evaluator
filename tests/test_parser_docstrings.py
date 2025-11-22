from pathlib import Path
from ccqe.parser import extract_python_entities


def test_extracts_module_class_method_and_function_docstrings(tmp_path: Path):
    code = '''\
"""Module docstring about configuration."""
class C:
    """Class docstring explaining why this wrapper exists."""
    def m(self):
        """Method docstring describing side effects."""
        return 1

def f():
    """Function docstring explaining constraints."""
    return 2
'''
    p = tmp_path / "docs_example.py"
    p.write_text(code, encoding="utf-8")

    spans, _ = extract_python_entities(p)
    texts = [s.text for s in spans]

    # We expect all four docstrings to be found
    assert any("Module docstring" in t for t in texts)
    assert any("Class docstring" in t for t in texts)
    assert any("Method docstring" in t for t in texts)
    assert any("Function docstring" in t for t in texts)
