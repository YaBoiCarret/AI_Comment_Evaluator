from pathlib import Path
from ccqe.cli import analyze_path


def test_cli_on_samples():
    project_root = Path(__file__).resolve().parents[1]
    samples = project_root / "samples"

    lines = analyze_path(samples)

    # Only treat lines with '|' as per-comment report lines
    # This skips the "Summary:" block at the end.
    report_lines = [ln for ln in lines if "|" in ln]

    # We expect at least one comment to be reported
    assert report_lines, "Expected at least one report line from samples"

    # Extract labels from the third '|' segment
    labels = [seg.split("|")[2].strip() for seg in report_lines]

    # All labels should be valid
    assert all(l in {"High", "Medium", "Low"} for l in labels)

    # We expect at least one low-quality comment from example_mixed.py
    assert any(l == "Low" for l in labels), "Expected at least one Low label in samples"

    # And at least one better-than-low comment (Medium or High) from the good example
    assert any(l in {"Medium", "High"} for l in labels), "Expected at least one Medium/High label in samples"

    # Optionally, also verify that the summary block exists
    summary_present = any(ln.strip() == "Summary:" for ln in lines)
    assert summary_present, "Expected a Summary block at the end of the report"