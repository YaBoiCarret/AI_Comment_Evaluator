from __future__ import annotations

import ast
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class CommentSpan:
    """
    A single comment-like region in a Python file.

    file    : path to the source file
    lineno  : line number where the comment or docstring begins
    text    : cleaned comment text (hash removed) or docstring content
    context : "inline" for line comments, "docstring" for docstrings
    func    : name of the enclosing function, if any
    cls     : name of the enclosing class, if any
    """
    file: Path
    lineno: int
    text: str
    context: str  # "inline" or "docstring"
    func: Optional[str] = None
    cls: Optional[str] = None


def extract_python_entities(path: Path) -> Tuple[List[CommentSpan], str]:
    """
    Extract inline comments and docstrings from a Python file.

    Returns:
        (spans, source) where spans is a list of CommentSpan objects
        and source is the full file content as a string.

    The function is resilient to syntax or tokenization errors: failures
    in one extraction step are swallowed so the caller still receives
    whatever information could be recovered.
    """
    src = path.read_text(encoding="utf-8", errors="ignore")

    inline: List[CommentSpan] = []
    try:
        # Use the tokenize module so we only treat true Python comments as inline
        # comments and ignore comment-like substrings in strings.
        from io import BytesIO

        for tok in tokenize.tokenize(BytesIO(src.encode("utf-8")).readline):
            if tok.type == tokenize.COMMENT:
                text = tok.string.lstrip("#").strip()
                if text:
                    inline.append(
                        CommentSpan(
                            file=path,
                            lineno=tok.start[0],
                            text=text,
                            context="inline",
                        )
                    )
    except Exception:
        # If tokenization fails (for example due to incomplete input),
        # continue and still attempt to extract docstrings via ast.parse.
        pass

    doc_spans: List[CommentSpan] = []
    try:
        tree = ast.parse(src)

        # Module docstring, if present.
        mdoc = ast.get_docstring(tree, clean=True)
        if mdoc:
            first = tree.body[0].lineno if tree.body else 1
            doc_spans.append(
                CommentSpan(
                    file=path,
                    lineno=first,
                    text=mdoc,
                    context="docstring",
                )
            )

        # Function, async function, and class docstrings discovered by walking the AST.
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                d = ast.get_docstring(node, clean=True)
                if d:
                    doc_spans.append(
                        CommentSpan(
                            file=path,
                            lineno=node.lineno,
                            text=d,
                            context="docstring",
                            func=node.name,
                        )
                    )
            elif isinstance(node, ast.ClassDef):
                d = ast.get_docstring(node, clean=True)
                if d:
                    doc_spans.append(
                        CommentSpan(
                            file=path,
                            lineno=node.lineno,
                            text=d,
                            context="docstring",
                            cls=node.name,
                        )
                    )
    except Exception:
        # If parsing fails (for example due to syntax errors), fall back
        # to inline comments only.
        pass

    return inline + doc_spans, src


def find_python_files(root: Path) -> List[Path]:
    """
    Recursively collect all Python source files under the given root directory.

    Only regular files with a .py extension are returned.
    """
    files: List[Path] = []
    for p in root.rglob("*.py"):
        if p.is_file():
            files.append(p)
    return files
