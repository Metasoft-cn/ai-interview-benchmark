"""Tests for perturbation generator."""
from aib.perturbation import (
    PerturbationConfig,
    generate_perturbations,
    paraphrase_case,
    verbosity_case,
    asr_noise_case,
)
import random


def _base_cases():
    return [
        {"case_id": "sc_001", "type": "scoring", "question": "请用一分钟介绍你自己",
         "answer": "我是一名有五年经验的后端工程师，主要负责过电商订单和支付系统。",
         "ground_truth_score": 84, "difficulty": "easy", "evidence": []},
        {"case_id": "sc_002", "type": "scoring", "question": "你为什么申请这个岗位",
         "answer": "因为贵公司的技术栈和我的经验高度匹配。",
         "ground_truth_score": 86, "difficulty": "easy", "evidence": []},
    ]


def test_generate_perturbations_basic():
    cases = _base_cases()
    config = PerturbationConfig(seed=42, paraphrase_per_base=2, verbosity_per_base=2, asr_noise_per_base=1)
    result = generate_perturbations(cases, config)
    assert len(result) == 10  # 2 bases × (2 paraphrase + 2 verbosity + 1 asr)


def test_perturbation_labels():
    cases = _base_cases()
    config = PerturbationConfig(seed=42)
    result = generate_perturbations(cases, config)
    for case in result:
        assert "label" in case
        assert case["label"] in ("curated", "template-derived", "synthetic")


def test_paraphrase_changes_question():
    base = _base_cases()[0]
    rng = random.Random(42)
    case = paraphrase_case(base, 0, rng)
    assert case is not None
    assert case["question"] != base["question"]
    assert case["perturbation"] == "paraphrase"
    assert case["expected_score"] == 84


def test_verbosity_preserves_question():
    base = _base_cases()[0]
    rng = random.Random(42)
    case = verbosity_case(base, 0, rng)
    assert case["question"] == base["question"]
    assert case["perturbation"] == "verbosity"


def test_asr_noise_label():
    base = _base_cases()[0]
    rng = random.Random(42)
    case = asr_noise_case(base, 0, rng)
    assert case["label"] == "synthetic"
    assert case["perturbation"] == "asr_noise"


def test_perturbation_deterministic():
    cases = _base_cases()
    config = PerturbationConfig(seed=42)
    r1 = generate_perturbations(cases, config)
    r2 = generate_perturbations(cases, config)
    assert r1 == r2


def test_perturbation_ids_unique():
    cases = _base_cases()
    config = PerturbationConfig(seed=42)
    result = generate_perturbations(cases, config)
    ids = [c["case_id"] for c in result]
    assert len(ids) == len(set(ids))
