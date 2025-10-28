
from __future__ import annotations
import ast
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

@dataclass
class CommentSpan:
    file: Path
    lineno: int
    text: str
    context: str  # "inline" or "docstring"
    func: Optional[str] = None
    cls: Optional[str] = None

def extract_python_entities(path: Path) -> Tuple[List[CommentSpan], str]:
    src = path.read_text(encoding="utf-8", errors="ignore")
    inline: List[CommentSpan] = []
    try:
        from io import BytesIO
        for tok in tokenize.tokenize(BytesIO(src.encode("utf-8")).readline):
            if tok.type == tokenize.COMMENT:
                text = tok.string.lstrip("#").strip()
                if text:
                    inline.append(CommentSpan(path, tok.start[0], text, "inline"))
    except Exception:
        pass

    doc_spans: List[CommentSpan] = []
    try:
        tree = ast.parse(src)
        mdoc = ast.get_docstring(tree, clean=True)
        if mdoc:
            first = tree.body[0].lineno if tree.body else 1
            doc_spans.append(CommentSpan(path, first, mdoc, "docstring"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                d = ast.get_docstring(node, clean=True)
                if d:
                    doc_spans.append(CommentSpan(path, node.lineno, d, "docstring", func=node.name))
            elif isinstance(node, ast.ClassDef):
                d = ast.get_docstring(node, clean=True)
                if d:
                    doc_spans.append(CommentSpan(path, node.lineno, d, "docstring", cls=node.name))
    except Exception:
        pass

    return inline + doc_spans, src

def find_python_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for p in root.rglob("*.py"):
        if p.is_file():
            files.append(p)
    return files
