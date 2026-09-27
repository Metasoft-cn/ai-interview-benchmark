"""Unit tests for AI Interview Benchmark metrics."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aib.metrics import (
    evidence_grounding,
    level_bias,
    mae,
    paraphrase_score_drift,
    ranking_consistency,
    stability_sigma,
)


def test_ranking_consistency_all_correct():
    scores = {("q", "good"): 80, ("q", "bad"): 30}
    cases = [{"question": "q", "answer_better": "good", "answer_worse": "bad"}]
    assert ranking_consistency(scores, cases) == 1.0


def test_ranking_consistency_all_wrong():
    scores = {("q", "good"): 30, ("q", "bad"): 80}
    cases = [{"question": "q", "answer_better": "good", "answer_worse": "bad"}]
    assert ranking_consistency(scores, cases) == 0.0


def test_ranking_consistency_empty():
    assert ranking_consistency({}, []) == 1.0


def test_mae():
    scores = {("q", "a1"): 80, ("q", "a2"): 30}
    cases = [
        {"question": "q", "answer": "a1", "ground_truth_score": 85},
        {"question": "q", "answer": "a2", "ground_truth_score": 25},
    ]
    assert mae(scores, cases) == 5.0


def test_stability_sigma_deterministic():
    assert stability_sigma([[80, 80, 80], [30, 30, 30]]) == 0.0


def test_stability_sigma_noisy():
    sig = stability_sigma([[80, 82, 78]])
    assert sig > 0


def test_level_bias_signs():
    scores = {("q", "a1"): 90, ("q", "a2"): 20}
    cases = [
        {"question": "q", "answer": "a1", "ground_truth_score": 85, "difficulty": "easy"},
        {"question": "q", "answer": "a2", "ground_truth_score": 25, "difficulty": "hard"},
    ]
    lb = level_bias(scores, cases)
    assert lb["easy"] == 5.0
    assert lb["hard"] == -5.0


def test_evidence_grounding_full():
    cited = {("q", "a"): ["e1", "e2"]}
    cases = [{"question": "q", "answer": "a", "evidence": ["e1", "e2"]}]
    assert evidence_grounding(cited, cases) == 1.0


def test_evidence_grounding_partial():
    cited = {("q", "a"): ["e1"]}
    cases = [{"question": "q", "answer": "a", "evidence": ["e1", "e2", "e3"]}]
    assert abs(evidence_grounding(cited, cases) - (1 / 3)) < 1e-9


def test_evidence_grounding_no_ground_truth():
    cited = {("q", "a"): []}
    cases = [{"question": "q", "answer": "a", "evidence": []}]
    assert evidence_grounding(cited, cases) == 1.0


def test_paraphrase_score_drift_zero():
    scores = {("q", "a"): 84}
    cases = [{"question": "q", "answer": "a", "expected_score": 84}]
    assert paraphrase_score_drift(scores, cases) == 0.0


def test_paraphrase_score_drift_nonzero():
    scores = {("q", "a"): 90}
    cases = [{"question": "q", "answer": "a", "expected_score": 80}]
    assert paraphrase_score_drift(scores, cases) == 10.0
