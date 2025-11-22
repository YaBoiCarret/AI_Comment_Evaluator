from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from .parser import CommentSpan

# Match simple word-like tokens in both comments and code.
WORD_RE = re.compile(r"[a-zA-Z_]+")

# Map digit literals to word forms so code like `== 0` can align
# with comments that talk about “zero” or “one”.
NUMBER_MAP = {
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine",
}

# Patterns that rewrite common arithmetic and comparison idioms into
# descriptive tokens. This helps the model detect semantic overlap
# between code such as `i += 1` and comments like “increment i”.
OPERATOR_PATTERNS = [
    # increments / decrements
    (r"\+\=\s*1", " increment "),
    (r"\+\s*1", " add_one "),
    (r"\-\=\s*1", " decrement "),
    (r"\-\s*1", " subtract_one "),

    # arithmetic operations
    (r"\*", " multiply "),
    (r"\/", " divide "),

    # simple comparisons against zero and one
    (r"==\s*0", " equals_zero "),
    (r"!=\s*0", " not_zero "),
    (r"==\s*1", " equals_one "),
]


def normalize_numbers(text: str) -> str:
    """
    Replace standalone digits with simple word forms.

    Word boundaries are used so that only numeric literals are affected,
    not digits that appear inside identifiers.
    """
    for num, word in NUMBER_MAP.items():
        text = re.sub(rf"\b{re.escape(num)}\b", f" {word} ", text)
    return text


def normalize_operations(text: str) -> str:
    """
    Replace common operator patterns with descriptive tokens.

    This gives the model a more “comment-like” representation of the code,
    which makes overlap with natural language comments easier to detect.
    """
    for pattern, replacement in OPERATOR_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text


def normalize_code_text(text: str) -> str:
    """
    Apply lightweight normalization to code before tokenization.

    The goal is to bridge the gap between code syntax and natural language
    comments so that semantically equivalent phrases share more tokens.
    """
    text = normalize_numbers(text)
    text = normalize_operations(text)
    return text


@dataclass
class PreparedComment:
    """
    Structured representation of a comment plus its local code context.

    span         : original CommentSpan describing location and raw text
    tokens       : tokenized comment text
    code_context : small window of nearby code, normalized for analysis
    """
    span: CommentSpan
    tokens: List[str]
    code_context: str


def tokenize_text(text: str) -> List[str]:
    """
    Extract lowercase word tokens from text using a simple regex.

    This is used for both comment text and normalized code context so that
    the model can compare them in a consistent token space.
    """
    return [m.group(0).lower() for m in WORD_RE.finditer(text)]


def build_prepared(span: CommentSpan, source: str) -> PreparedComment:
    """
    Build a PreparedComment from a raw CommentSpan and full source text.

    A small window of lines around the comment is extracted as the code
    context and normalized so that the model can reason about semantic
    redundancy between the comment and the surrounding code.
    """
    lines = source.splitlines()
    i = max(0, span.lineno - 2)
    j = min(len(lines), span.lineno + 1)
    context = "\n".join(lines[i:j])

    context = normalize_code_text(context)
    tokens = tokenize_text(span.text)

    return PreparedComment(span=span, tokens=tokens, code_context=context)
