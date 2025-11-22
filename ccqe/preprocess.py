from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List
from .parser import CommentSpan

WORD_RE = re.compile(r"[a-zA-Z_]+")

@dataclass
class PreparedComment:
    span: CommentSpan
    tokens: List[str]
    code_context: str

def tokenize_text(text: str) -> List[str]:
    return [m.group(0).lower() for m in WORD_RE.finditer(text)]

def build_prepared(span: CommentSpan, source: str) -> PreparedComment:
    lines = source.splitlines()
    i = max(0, span.lineno - 2)
    j = min(len(lines), span.lineno + 1)
    context = "\n".join(lines[i:j])
    tokens = tokenize_text(span.text)
    return PreparedComment(span, tokens, context)
