
# CCQE — Code Comment Quality Evaluator (Prototype)

A small, explainable tool that evaluates the usefulness of Python code comments and offers suggestions.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .[dev]
python -m ccqe.cli --path samples
```

## Run tests

```bash
pytest -q
```

## How it works

- Parses Python files to collect inline comments and docstrings.
- Builds simple text features and compares comments to nearby code.
- Predicts quality with heuristics and explains how to improve.
