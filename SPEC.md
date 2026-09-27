# AI Interview Benchmark — Specification

**Version:** 0.1.0-draft
**Protocol:** MBP v0.1.0-draft

## 1. Object of evaluation

The system under test is an **answer evaluator**: a function that takes a question and an answer and returns a score, feedback, and cited evidence. AIB measures whether the evaluator is stable, consistent, unbiased, and grounded.

AIB does **not** evaluate job candidates. All answers are authored or perturbation-derived; no real personal data is used.

## 2. Adapter contract

```
evaluate(question: str, answer: str) -> {
    "score": float,          # 0..100
    "feedback": str,
    "cited_evidence": [str]
}
```

## 3. Dataset

Three case types:

- **scoring**: `{case_id, type, question, answer, ground_truth_score, difficulty, evidence}` — the evaluator's score is compared to `ground_truth_score`.
- **ranking**: `{case_id, type, question, answer_better, answer_worse}` — the evaluator must score `answer_better` higher.
- **perturbation**: `{case_id, type, base_case_id, perturbation, question, answer, expected_score}` — a meaning-preserving perturbation (paraphrase, verbosity, asr_noise); the evaluator's score should not drift from `expected_score`.

Cases are `curated` (authored) or `template-derived` (perturbations of curated cases). The split is recorded per case. v0.1 has 24 cases; the target is 100–300 curated cases before preview freeze.

## 4. Metrics

See [`METRICS.md`](METRICS.md). All are pure functions with unit tests in [`tests/test_metrics.py`](tests/test_metrics.py).

## 5. Invariance properties

- **Paraphrase invariance:** a reworded answer with the same meaning should score the same.
- **Verbosity invariance:** a shorter or longer answer with the same facts should not score differently solely due to length.
- **ASR-noise robustness:** minor recognition noise should not destabilize the score.

These are tested via perturbation cases and `paraphrase_score_drift`.

## 6. Open vs hidden

v0.1 is `OPEN_SUITE`. A `HIDDEN_HOLDOUT` is reserved so the evaluator cannot be tuned against public cases in the future. No holdout data is included yet.

## 7. No candidate ranking

AIB compares evaluation systems, not candidates. Data is synthetic/curated/de-identified. No real personal privacy is imported.

## 8. MBP conformance

- `benchmark-manifest.json` validates against MBP `benchmark.schema.json`.
- `datasets/MANIFEST.json` validates against MBP `dataset-manifest.schema.json`.
- Results are multi-dimensional with a failure-first orientation (per-case drift and bias are reported, not just aggregates).
- Freeze state: `DRAFT`.
