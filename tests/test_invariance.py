"""Invariance tests: an ideal evaluator (returns ground truth) must not drift
on perturbation cases, and must be perfectly stable."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aib.metrics import paraphrase_score_drift, stability_sigma
from aib.runner import load_jsonl


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
