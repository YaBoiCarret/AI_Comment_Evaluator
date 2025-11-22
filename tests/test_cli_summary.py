from pathlib import Path
from ccqe.cli import analyze_path


def test_summary_block_counts_single_file(tmp_path: Path):
    # Create a tiny Python file with one weak inline comment
    code = """\
# repeats code
def add_one(x):
    # add one
    return x + 1
"""
    p = tmp_path / "sample.py"
    p.write_text(code, encoding="utf-8")

    lines = analyze_path(tmp_path)

    # Summary block should be present at the end
    assert any(ln.strip() == "Summary:" for ln in lines)

    # Extract summary lines only
    summary_lines = [ln for ln in lines if ln.startswith("Summary:") or ln.strip().startswith(("Files processed:", "Comments analyzed:", "High:", "Medium:", "Low:", "Avg redundancy:", "Suggestions asking for intent:"))]

    # Basic sanity checks on counts
    # Files processed: 1
    assert any("Files processed:" in ln and "1" in ln for ln in lines)
    # Comments analyzed: at least 1
    assert any("Comments analyzed:" in ln for ln in lines)

    # At least one Low label from this obviously bad comment
    report_lines = [ln for ln in lines if "|" in ln]
    labels = [seg.split("|")[2].strip() for seg in report_lines]
    assert any(l == "Low" for l in labels)
