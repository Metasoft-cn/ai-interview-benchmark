"""AI Interview Benchmark metrics.

Each metric is a pure function with a docstring stating its definition.
These are the five metrics reused from the existing product evaluator
(ranking consistency, MAE, stability sigma, level bias, evidence grounding),
implemented as standalone, deterministic, testable code.
"""
import statistics


def ranking_consistency(scores, ranking_cases):
    """Fraction of ranking cases where score(answer_better) > score(answer_worse).

    A correct evaluator ranks a better answer above a worse one.
    Returns 1.0 when there are no ranking cases.
    """
    if not ranking_cases:
        return 1.0
    correct = 0
    for c in ranking_cases:
        sb = scores.get((c["question"], c["answer_better"]))
        sw = scores.get((c["question"], c["answer_worse"]))
        if sb is not None and sw is not None and sb > sw:
            correct += 1
    return correct / len(ranking_cases)


def mae(scores, scoring_cases):
    """Mean absolute error between adapter score and ground-truth score.

    Lower is better. Range [0, 100].
    """
    errs = []
    for c in scoring_cases:
        s = scores.get((c["question"], c["answer"]))
        if s is not None:
            errs.append(abs(s - c["ground_truth_score"]))
    return statistics.mean(errs) if errs else 0.0


def stability_sigma(score_sequences):
    """Mean per-case standard deviation of repeated scores.

    score_sequences: list of lists, each inner list is repeated scores for one case.
    Lower is better. A deterministic evaluator returns 0.
    """
    sigs = [statistics.stdev(seq) for seq in score_sequences if len(seq) > 1]
    return statistics.mean(sigs) if sigs else 0.0


def level_bias(scores, scoring_cases):
    """Per-difficulty mean signed error (adapter_score - ground_truth).

    Returns a dict difficulty -> mean signed error. A positive value means the
    adapter over-scores that difficulty band; negative means under-scores.
    """
    by_diff = {}
    for c in scoring_cases:
        s = scores.get((c["question"], c["answer"]))
        if s is not None:
            by_diff.setdefault(c["difficulty"], []).append(s - c["ground_truth_score"])
    return {d: statistics.mean(v) for d, v in by_diff.items()}


def evidence_grounding(cited, scoring_cases):
    """Mean fraction of ground-truth evidence cited by the adapter.

    cited: dict (question, answer) -> list of cited evidence strings.
    A case with no ground-truth evidence counts as fully grounded (1.0).
    """
    fracs = []
    for c in scoring_cases:
        gt = set(c.get("evidence", []))
        ci = set(cited.get((c["question"], c["answer"]), []))
        if gt:
            fracs.append(len(gt & ci) / len(gt))
        else:
            fracs.append(1.0)
    return statistics.mean(fracs) if fracs else 0.0


def paraphrase_score_drift(scores, perturbation_cases):
    """Mean absolute score change between a perturbation case and its base expected score.

    For paraphrase/verbosity/asr_noise perturbations, a robust evaluator's score
    should not drift. Lower is better.
    """
    drifts = []
    for c in perturbation_cases:
        s = scores.get((c["question"], c["answer"]))
        if s is not None and "expected_score" in c:
            drifts.append(abs(s - c["expected_score"]))
    return statistics.mean(drifts) if drifts else 0.0
