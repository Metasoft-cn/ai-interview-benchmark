"""Generate AIB v0.2 preview freeze artifacts.

Run this script to produce:
  - datasets/splits/{train,dev,public_test,hidden_test}.jsonl
  - invariance/invariance_cases.jsonl
  - hidden/HOLDOUT_MANIFEST.json
  - benchmark-manifest-v0.2.json
  - reports/AIB_PREVIEW_REPORT.md
"""
from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aib.perturbation import PerturbationConfig, generate_perturbations, file_sha256, write_jsonl
from aib.invariance import INVARIANCE_GROUPS, export_invariance_cases, evaluate_invariance, invariance_summary
from aib.split import SplitConfig, split_dataset, write_splits, load_jsonl
from aib.baselines import BASELINES


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_dir = os.path.join(base_dir, "datasets")

    # 1. Load base cases
    scoring = load_jsonl(os.path.join(datasets_dir, "scoring.jsonl"))
    ranking = load_jsonl(os.path.join(datasets_dir, "ranking.jsonl"))
    perturbation = load_jsonl(os.path.join(datasets_dir, "perturbation.jsonl"))
    base_cases = scoring + ranking + perturbation

    # 2. Generate perturbations
    pert_config = PerturbationConfig(seed=20260927)
    generated = generate_perturbations(base_cases, pert_config)

    # 3. Split dataset
    split_config = SplitConfig(seed=20260927)
    splits = split_dataset(base_cases, split_config, pert_config)
    splits_dir = os.path.join(datasets_dir, "splits")
    split_manifest = write_splits(splits, splits_dir)

    # 4. Export invariance cases
    inv_path = os.path.join(base_dir, "invariance", "invariance_cases.jsonl")
    export_invariance_cases(inv_path)
    inv_cases = load_jsonl(inv_path)

    # 5. Hidden holdout manifest
    hidden_dir = os.path.join(base_dir, "hidden")
    os.makedirs(hidden_dir, exist_ok=True)
    hidden_cases = splits["hidden_test"]
    hidden_jsonl = os.path.join(hidden_dir, "hidden_test.jsonl")
    write_jsonl(hidden_cases, hidden_jsonl)
    holdout_manifest = {
        "holdout_version": "0.2.0-preview.1",
        "case_count": len(hidden_cases),
        "sha256": file_sha256(hidden_jsonl),
        "released": False,
        "description": "Hidden holdout for MBP Verified Score. Not released publicly.",
    }
    with open(os.path.join(hidden_dir, "HOLDOUT_MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(holdout_manifest, f, indent=2, ensure_ascii=False)

    # 6. Run invariance evaluation on all baselines
    inv_results = {}
    for name, fn in BASELINES.items():
        results = evaluate_invariance(fn)
        inv_results[name] = invariance_summary(results)

    # 7. Compute dataset hash
    all_cases = base_cases + generated
    h = hashlib.sha256()
    for case in sorted(all_cases, key=lambda c: c["case_id"]):
        h.update(json.dumps(case, sort_keys=True, ensure_ascii=False).encode("utf-8"))
        h.update(b"\n")
    dataset_hash = h.hexdigest()

    # 8. v0.2 manifest
    total_cases = len(all_cases) + len(inv_cases)
    manifest_v02 = {
        "benchmark": {
            "id": "ai-interview",
            "name": "AI Interview Benchmark",
            "version": "0.2.0-preview.1",
            "protocol_version": "0.1.0-draft",
            "mode": "OPEN_SUITE",
            "domain": "interview-evaluation",
        },
        "dataset": {
            "version": "0.2.0-preview.1",
            "cases": total_cases,
            "events": total_cases,
            "hash": dataset_hash,
            "seed": 20260927,
        },
        "splits": {
            "train": split_manifest["train"],
            "dev": split_manifest["dev"],
            "public_test": split_manifest["public_test"],
            "hidden_test": {
                **split_manifest["hidden_test"],
                "released": False,
            },
        },
        "invariance": {
            "groups": len(INVARIANCE_GROUPS),
            "cases": len(inv_cases),
            "sha256": file_sha256(inv_path),
        },
        "perturbation": {
            "generated_count": len(generated),
            "types": ["paraphrase", "verbosity", "asr_noise"],
            "labels": ["curated", "template-derived", "synthetic"],
        },
        "runner": {"version": "0.2.0"},
        "metrics": {"version": "0.2.0"},
        "baselines": [
            {"id": "length", "version": "0.2.0"},
            {"id": "keyword", "version": "0.2.0"},
            {"id": "constant", "version": "0.2.0"},
        ],
    }
    manifest_path = os.path.join(base_dir, "benchmark-manifest-v0.2.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_v02, f, indent=2, ensure_ascii=False)

    # 9. Preview report
    report_path = os.path.join(base_dir, "reports", "AIB_PREVIEW_REPORT.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    lines = []
    lines.append("# AIB v0.2 Preview Report")
    lines.append("")
    lines.append("**Status:** PREVIEW (frozen)")
    lines.append(f"**Dataset hash:** `{dataset_hash}`")
    lines.append(f"**Total cases:** {total_cases} ({len(base_cases)} curated + {len(generated)} generated + {len(inv_cases)} invariance)")
    lines.append("")
    lines.append("## Dataset Splits")
    lines.append("")
    lines.append("| Split | Cases | Released |")
    lines.append("|-------|-------|----------|")
    for name in ["train", "dev", "public_test", "hidden_test"]:
        released = "Yes" if name != "hidden_test" else "**No**"
        lines.append(f"| {name} | {split_manifest[name]['case_count']} | {released} |")
    lines.append("")
    lines.append("## Perturbation Coverage")
    lines.append("")
    ptypes = {}
    for c in generated:
        ptypes[c["perturbation"]] = ptypes.get(c["perturbation"], 0) + 1
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    for t, n in sorted(ptypes.items()):
        lines.append(f"| {t} | {n} |")
    lines.append("")
    lines.append("## Invariance Test")
    lines.append("")
    lines.append(f"Groups: {len(INVARIANCE_GROUPS)}")
    lines.append(f"Cases: {len(inv_cases)}")
    lines.append("")
    lines.append("### Baseline Invariance Results")
    lines.append("")
    lines.append("| Baseline | Pass Rate | Mean Drift | Max Drift | Failed Groups |")
    lines.append("|----------|-----------|-----------|-----------|---------------|")
    for name, summary in inv_results.items():
        lines.append(f"| {name} | {summary['pass_rate']:.1%} | {summary['mean_drift']:.2f} | {summary['max_drift']:.2f} | {summary['failed']} |")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("1. ranking_consistency — fraction of ranking cases correct")
    lines.append("2. mae — mean absolute error")
    lines.append("3. stability_sigma — mean per-case stdev")
    lines.append("4. level_bias — per-difficulty signed error")
    lines.append("5. evidence_grounding — mean evidence recall")
    lines.append("6. paraphrase_score_drift — mean perturbation drift")
    lines.append("")
    lines.append("## Hidden Holdout")
    lines.append("")
    lines.append(f"- Cases: {len(hidden_cases)}")
    lines.append(f"- SHA256: `{holdout_manifest['sha256']}`")
    lines.append("- Released: **No** (MBP Verified Score only)")
    lines.append("")
    lines.append("## Methodology")
    lines.append("")
    lines.append("This benchmark follows the MBP evaluation methodology:")
    lines.append("1. **Dataset split** — train/dev/public_test/hidden_test prevents overfitting")
    lines.append("2. **Perturbation generator** — paraphrase/verbosity/asr_noise test semantic understanding")
    lines.append("3. **Invariance test** — same capability, different expression → scores should be close")
    lines.append("4. **Hidden holdout** — MBP Public Score vs MBP Verified Score")
    lines.append("")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated {total_cases} total cases")
    print(f"Splits: {', '.join(f'{n}={len(splits[n])}' for n in ['train','dev','public_test','hidden_test'])}")
    print(f"Perturbations: {len(generated)}")
    print(f"Invariance: {len(inv_cases)} cases in {len(INVARIANCE_GROUPS)} groups")
    print(f"Manifest: {manifest_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
