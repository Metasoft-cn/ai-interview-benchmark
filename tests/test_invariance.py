"""Invariance tests: an ideal evaluator (returns ground truth) must not drift
on perturbation cases, and must be perfectly stable.

v0.2 additions: invariance group evaluator tests.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aib.metrics import paraphrase_score_drift, stability_sigma
from aib.runner import load_jsonl
from aib.invariance import (
    INVARIANCE_GROUPS,
    evaluate_invariance,
    invariance_summary,
    export_invariance_cases,
)


def _datasets_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets")


def ideal_evaluator(question, answer, _gt=None):
    """Returns a fixed score; used to verify invariance metrics behave correctly."""
    return {"score": 50.0, "feedback": "", "cited_evidence": []}


def test_perturbation_cases_have_expected_score():
    perturbation = load_jsonl(os.path.join(_datasets_dir(), "perturbation.jsonl"))
    for c in perturbation:
        assert "expected_score" in c
        assert c["perturbation"] in ("paraphrase", "verbosity", "asr_noise")


def test_ideal_evaluator_zero_drift():
    perturbation = load_jsonl(os.path.join(_datasets_dir(), "perturbation.jsonl"))
    scores = {(c["question"], c["answer"]): c["expected_score"] for c in perturbation}
    assert paraphrase_score_drift(scores, perturbation) == 0.0


def test_deterministic_evaluator_zero_sigma():
    seqs = [[50.0, 50.0, 50.0] for _ in range(5)]
    assert stability_sigma(seqs) == 0.0


def test_scoring_cases_cover_difficulties():
    scoring = load_jsonl(os.path.join(_datasets_dir(), "scoring.jsonl"))
    diffs = {c["difficulty"] for c in scoring}
    assert diffs == {"easy", "medium", "hard"}


# --- v0.2 invariance group tests ---

def _keyword_adapter(question, answer):
    if "介绍" in question:
        return {"score": 90.0}
    if "为什么" in question:
        return {"score": 40.0}
    return {"score": 60.0}


def test_invariance_groups_defined():
    assert len(INVARIANCE_GROUPS) == 6
    for g in INVARIANCE_GROUPS:
        assert "group_id" in g
        assert "capability" in g
        assert len(g["questions"]) >= 3
        assert "max_acceptable_drift" in g


def test_constant_adapter_passes_invariance():
    results = evaluate_invariance(ideal_evaluator)
    assert all(r.passed for r in results)
    assert all(r.drift == 0.0 for r in results)


def test_keyword_adapter_fails_invariance():
    results = evaluate_invariance(_keyword_adapter)
    failed = [r for r in results if not r.passed]
    assert len(failed) > 0


def test_invariance_summary():
    results = evaluate_invariance(ideal_evaluator)
    summary = invariance_summary(results)
    assert summary["total_groups"] == 6
    assert summary["passed"] == 6
    assert summary["failed"] == 0
    assert summary["pass_rate"] == 1.0


def test_invariance_summary_with_failures():
    results = evaluate_invariance(_keyword_adapter)
    summary = invariance_summary(results)
    assert summary["failed"] > 0
    assert len(summary["failures"]) > 0


def test_export_invariance_cases(tmp_path):
    path = tmp_path / "invariance.jsonl"
    export_invariance_cases(str(path))
    import json
    lines = path.read_text(encoding="utf-8").strip().split("\n")
    cases = [json.loads(l) for l in lines]
    assert len(cases) > 0
    assert all(c["type"] == "invariance" for c in cases)
    assert all("group_id" in c for c in cases)
