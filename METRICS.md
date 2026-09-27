# AI Interview Benchmark — Metrics

All metrics are pure functions in [`aib/metrics.py`](../aib/metrics.py) with unit tests in [`tests/test_metrics.py`](../tests/test_metrics.py).

## 1. Ranking Consistency

**Definition:** fraction of ranking cases where `score(answer_better) > score(answer_worse)`.

**Range:** [0, 1]. Higher is better. 1.0 means the evaluator always orders correctly.

**Why:** an evaluator that cannot rank a better answer above a worse one is broken regardless of its absolute scores.

## 2. MAE (Mean Absolute Error)

**Definition:** mean of `|adapter_score - ground_truth_score|` over scoring cases.

**Range:** [0, 100]. Lower is better.

**Why:** measures agreement with human ground-truth scoring.

## 3. Stability Sigma

**Definition:** mean per-case standard deviation of repeated scores.

**Range:** [0, ∞). Lower is better. 0 means deterministic.

**Why:** an evaluator that gives different scores to the same answer on repeated calls is unreliable.

## 4. Level Bias

**Definition:** per-difficulty mean signed error `(adapter_score - ground_truth_score)`.

**Output:** dict `{easy, medium, hard} -> mean signed error`. Positive = over-scoring that band; negative = under-scoring.

**Why:** an evaluator that systematically over-scores easy answers and under-scores hard ones has a difficulty bias, even if its MAE looks acceptable.

## 5. Evidence Grounding

**Definition:** mean fraction of ground-truth evidence points cited by the adapter.

**Range:** [0, 1]. Higher is better. Cases with no ground-truth evidence count as 1.0.

**Why:** feedback that does not reference the facts that justify the score is filler, not evaluation.

## 6. Paraphrase Score Drift

**Definition:** mean `|adapter_score - expected_score|` over perturbation cases.

**Range:** [0, 100]. Lower is better. 0 means the evaluator is invariant to the perturbation.

**Why:** a meaning-preserving perturbation (paraphrase, verbosity, ASR noise) should not change the score. Drift reveals sensitivity to wording rather than content.

## No composite score

AIB does not compute a single aggregate. An evaluator with good MAE but poor ranking consistency is not "good overall"; it is broken in a specific way. Report all six metrics.
