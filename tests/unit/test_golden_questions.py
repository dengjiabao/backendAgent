import json
from pathlib import Path


def test_golden_questions_are_valid_and_include_forbidden_case():
    path = Path("evals/golden_questions.jsonl")
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(cases) >= 3
    assert any(case["expected_security"] == "blocked" for case in cases)
