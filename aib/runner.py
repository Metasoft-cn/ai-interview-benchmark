"""Runner: load cases, run an adapter, compute metrics."""
import json

from .baselines import BASELINES
from .metrics import (
    evidence_grounding,
    level_bias,
    mae,
    paraphrase_score_drift,
    ranking_consistency,
    stability_sigma,
)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_adapter(adapter, scoring, ranking, perturbation, n_repeats=3):
    """Run a callable adapter over all cases and compute the metric set."""
    scores = {}
    cited = {}
    seqs = []
    for c in scoring:
        key = (c["question"], c["answer"])
        seq = [adapter(c["question"], c["answer"])["score"] for _ in range(n_repeats)]
        scores[key] = seq[0]
        cited[key] = adapter(c["question"], c["answer"]).get("cited_evidence", [])
        seqs.append(seq)
    for c in ranking:
        for ans in (c["answer_better"], c["answer_worse"]):
            key = (c["question"], ans)
            if key not in scores:
                scores[key] = adapter(c["question"], ans)["score"]
    for c in perturbation:
        key = (c["question"], c["answer"])
        seq = [adapter(c["question"], c["answer"])["score"] for _ in range(n_repeats)]
        scores[key] = seq[0]
        seqs.append(seq)
    return {
        "ranking_consistency": ranking_consistency(scores, ranking),
        "mae": mae(scores, scoring),
        "stability_sigma": stability_sigma(seqs),
        "level_bias": level_bias(scores, scoring),
        "evidence_grounding": evidence_grounding(cited, scoring),
        "paraphrase_score_drift": paraphrase_score_drift(scores, perturbation),
    }


def run_all(scoring, ranking, perturbation):
    """Run all built-in baselines and return a dict name -> metrics."""
    results = {}
    for name, fn in BASELINES.items():
        results[name] = run_adapter(fn, scoring, ranking, perturbation)
    return results
