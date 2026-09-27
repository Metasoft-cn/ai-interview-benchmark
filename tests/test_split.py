"""Tests for dataset split."""
import json
import os

from aib.split import (
    SplitConfig,
    split_dataset,
    write_splits,
    load_jsonl,
    SPLIT_NAMES,
)
from aib.perturbation import PerturbationConfig


def _base_cases():
    return [
        {"case_id": f"sc_{i:03d}", "type": "scoring", "question": "q", "answer": "a",
         "ground_truth_score": 50, "difficulty": "easy", "evidence": []}
        for i in range(12)
    ] + [
        {"case_id": f"rk_{i:03d}", "type": "ranking", "question": "q",
         "answer_better": "good", "answer_worse": "bad"}
        for i in range(6)
    ] + [
        {"case_id": f"pt_{i:03d}", "type": "perturbation", "base_case_id": "sc_001",
         "perturbation": "paraphrase", "question": "q", "answer": "a", "expected_score": 50}
        for i in range(6)
    ]


def test_split_covers_all_cases():
    base = _base_cases()
    config = SplitConfig(seed=42)
    splits = split_dataset(base, config)
    total = sum(len(s) for s in splits.values())
    assert total > len(base)  # includes generated perturbations


def test_split_names():
    base = _base_cases()
    splits = split_dataset(base)
    assert set(splits.keys()) == set(SPLIT_NAMES)


def test_split_deterministic():
    base = _base_cases()
    config = SplitConfig(seed=42)
    s1 = split_dataset(base, config)
    s2 = split_dataset(base, config)
    for name in SPLIT_NAMES:
        assert s1[name] == s2[name]


def test_write_splits(tmp_path):
    base = _base_cases()
    config = SplitConfig(seed=42)
    splits = split_dataset(base, config)
    manifest = write_splits(splits, str(tmp_path))

    for name in SPLIT_NAMES:
        assert f"{name}.jsonl" in os.listdir(tmp_path)
        assert manifest[name]["case_count"] == len(splits[name])
        assert len(manifest[name]["sha256"]) == 64


def test_no_case_in_multiple_splits():
    base = _base_cases()
    splits = split_dataset(base)
    all_ids = []
    for cases in splits.values():
        all_ids.extend(c["case_id"] for c in cases)
    assert len(all_ids) == len(set(all_ids))
