import argparse
from collections import defaultdict
from pathlib import Path

from .parser import extract_python_entities
from .preprocess import build_prepared
from .model import predict_quality
from .feedback import suggestion_from


def analyze_path(path: str | Path) -> list[str]:
    """
    Analyze all Python files under the given path and return report lines.

    Each comment or docstring produces a single formatted report line that
    includes file, line number, inferred context, quality label, score,
    and a short suggestion. At the end of the list a summary section is
    appended with aggregate statistics about the run.
    """
    root = Path(path)
    if root.is_file() and root.suffix == ".py":
        files = [root]
    else:
        files = sorted(root.rglob("*.py"))

    lines: list[str] = []

    # Running statistics used to build the summary block
    seen_files: set[Path] = set()
    total_comments = 0
    label_counts: dict[str, int] = defaultdict(int)
    redundancy_sum = 0.0
    redundancy_count = 0
    needs_intent_count = 0

    for file in files:
        spans, source = extract_python_entities(file)
        if spans:
            seen_files.add(file)

        for span in spans:
            total_comments += 1

            prepared = build_prepared(span, source)
            quality = predict_quality(prepared)
            suggestion = suggestion_from(quality)

            label_counts[quality.label] += 1

            # Redundancy is tracked so we can report an average across all comments
            red = float(quality.signals.get("redundancy", 0.0) or 0.0)
            redundancy_sum += red
            redundancy_count += 1

            # Suggestions that ask for "intent" or "reason" highlight places where
            # comments explain what the code does but not why it exists
            s_lower = suggestion.lower()
            if "intent" in s_lower or "reason" in s_lower:
                needs_intent_count += 1

            ctx = span.func or span.cls or span.file.name
            lines.append(
                f"{span.file}: {span.lineno:3d} | {ctx:<15} | "
                f"{quality.label:<6} | score={quality.score:.2f} | {suggestion}"
            )

    summary_lines: list[str] = []
    summary_lines.append("")  # separate the detailed report from the summary
    summary_lines.append("Summary:")
    summary_lines.append(f"  Files processed: {len(seen_files)}")
    summary_lines.append(f"  Comments analyzed: {total_comments}")
    for label in ("High", "Medium", "Low"):
        summary_lines.append(f"  {label}: {label_counts.get(label, 0)}")

    if redundancy_count:
        avg_red = redundancy_sum / redundancy_count
        summary_lines.append(f"  Avg redundancy: {avg_red:.2f}")

    if total_comments:
        pct_intent = 100.0 * needs_intent_count / total_comments
        summary_lines.append(
            "  Suggestions asking for intent: "
            f"{needs_intent_count} ({pct_intent:.1f}% of comments)"
        )

    return lines + summary_lines


def main() -> None:
    """
    Parse command line arguments, run the analyzer, and print a report.

    This function is the user facing entry point when the module is invoked
    as a script. It accepts a single --path argument and prints either a
    detailed report or a short message if no comments are found.
    """
    ap = argparse.ArgumentParser(
        description="Code Comment Quality Evaluator (prototype)"
    )
    ap.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to a Python file or directory",
    )
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
