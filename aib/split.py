"""Dataset split for AIB v0.2.

Splits the full dataset (curated + generated perturbations + invariance)
into four splits:

  train        — for participants to calibrate (public)
  dev          — for development (public)
  public_test  — the reported public score (public)
  hidden_test  — the verified score (NOT released)

The split is deterministic (hash-based assignment, fixed proportions).
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any

from .perturbation import (
    PerturbationConfig,
    generate_perturbations,
    write_jsonl,
    file_sha256,
)


@dataclass
class SplitConfig:
    train_ratio: float = 0.15
    dev_ratio: float = 0.15
    public_test_ratio: float = 0.35
    hidden_test_ratio: float = 0.35
    seed: int = 20260927


SPLIT_NAMES = ["train", "dev", "public_test", "hidden_test"]


def _assign_split(case_id: str, config: SplitConfig) -> str:
    h = hashlib.sha256(f"{case_id}:{config.seed}".encode()).hexdigest()
    val = int(h[:8], 16) / 0xFFFFFFFF

    cumul = 0.0
    ratios = [
        ("train", config.train_ratio),
        ("dev", config.dev_ratio),
        ("public_test", config.public_test_ratio),
        ("hidden_test", config.hidden_test_ratio),
    ]
    for name, ratio in ratios:
        cumul += ratio
        if val < cumul:
            return name
    return "hidden_test"


def split_dataset(
    base_cases: list[dict[str, Any]],
    config: SplitConfig | None = None,
    perturbation_config: PerturbationConfig | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Split the full dataset into train/dev/public_test/hidden_test.

    Args:
        base_cases: the original curated cases (scoring + ranking + perturbation).
        config: split proportions.
        perturbation_config: perturbation generation config.

    Returns:
        dict split_name -> list of cases.
    """
    config = config or SplitConfig()
    perturbation_config = perturbation_config or PerturbationConfig()

    generated = generate_perturbations(base_cases, perturbation_config)

    all_cases = list(base_cases) + generated

    splits: dict[str, list[dict[str, Any]]] = {name: [] for name in SPLIT_NAMES}
    for case in all_cases:
        split_name = _assign_split(case["case_id"], config)
        splits[split_name].append(case)

    return splits


def write_splits(
    splits: dict[str, list[dict[str, Any]]],
    output_dir: str,
) -> dict[str, dict[str, Any]]:
    """Write split files and return manifest metadata.

    Returns:
        dict split_name -> {path, sha256, case_count, bytes}
    """
    os.makedirs(output_dir, exist_ok=True)
    manifest: dict[str, dict[str, Any]] = {}

    for name, cases in splits.items():
        path = os.path.join(output_dir, f"{name}.jsonl")
        write_jsonl(cases, path)
        size = os.path.getsize(path)
        manifest[name] = {
            "path": f"datasets/splits/{name}.jsonl",
            "sha256": file_sha256(path),
            "case_count": len(cases),
            "bytes": size,
        }

    return manifest


def load_jsonl(path: str) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
