"""AI Interview Benchmark CLI."""
import argparse
import json
import os

from .runner import load_jsonl, run_all


def _datasets_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets")


def cmd_validate(args):
    d = _datasets_dir()
    files = ["scoring.jsonl", "ranking.jsonl", "perturbation.jsonl"]
    total = 0
    for fn in files:
        cases = load_jsonl(os.path.join(d, fn))
        total += len(cases)
        print(f"{fn}: {len(cases)} cases")
    print(f"total: {total} cases")
    m = json.load(open(os.path.join(d, "MANIFEST.json"), encoding="utf-8"))
    assert m["case_count"] == total, f"manifest count {m['case_count']} != actual {total}"
    print(json.dumps({"cases": total, "dataset_version": m["dataset_version"]}, indent=2))


def cmd_run(args):
    d = _datasets_dir()
    scoring = load_jsonl(os.path.join(d, "scoring.jsonl"))
    ranking = load_jsonl(os.path.join(d, "ranking.jsonl"))
    perturbation = load_jsonl(os.path.join(d, "perturbation.jsonl"))
    if args.quick:
        scoring = scoring[:10]
        ranking = ranking[:5]
        perturbation = perturbation[:5]
    results = run_all(scoring, ranking, perturbation)
    for name, m in results.items():
        parts = [f"{k}={v:.4f}" for k, v in m.items() if k != "level_bias"]
        print(f"{name}: " + " ".join(parts))


def main():
    p = argparse.ArgumentParser(prog="aib")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate").set_defaults(func=cmd_validate)
    r = sub.add_parser("run")
    r.add_argument("--quick", action="store_true")
    r.set_defaults(func=cmd_run)
    args = p.parse_args()
    args.func(args)
