from pathlib import Path
from ccqe.cli import analyze_path

def test_cli_on_samples(tmp_path: Path):
    # Point the analyzer at the bundled samples folder
    project_root = Path(__file__).resolve().parents[1]
    samples = project_root / "samples"

    lines = analyze_path(samples)
    assert lines, "Expected at least one report line"
    # Should produce a mix of labels on the mixed sample
    labels = [seg.split("|")[2].strip() for seg in lines]
    assert any(l == "High" for l in labels)
    assert any(l in {"Medium", "Low"} for l in labels)
