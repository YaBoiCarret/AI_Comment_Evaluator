
from __future__ import annotations
import argparse
from pathlib import Path
from typing import List
from .parser import find_python_files, extract_python_entities
from .preprocess import build_prepared
from .model import predict_quality
from .feedback import suggestion_from

def analyze_path(path: Path) -> List[str]:
    out_lines: List[str] = []
    files = [path] if path.is_file() else find_python_files(path)
    for f in files:
        spans, src = extract_python_entities(f)
        for sp in spans:
            pc = build_prepared(sp, src)
            q = predict_quality(pc)
            ctx = sp.func or sp.cls or f.name
            out_lines.append(f"{f}:{sp.lineno:>4} | {ctx:15} | {q.label:<6} | score={q.score:.2f} | {suggestion_from(q)}")
    return out_lines

def main():
    ap = argparse.ArgumentParser(description="Code Comment Quality Evaluator (prototype)")
    ap.add_argument("--path", type=str, required=True, help="Path to a Python file or directory")
    args = ap.parse_args()
    path = Path(args.path)
    lines = analyze_path(path)
    if not lines:
        print("No comments or docstrings found.")
        return
    print("Report:")
    for line in lines:
        print(line)

if __name__ == "__main__":
    main()
