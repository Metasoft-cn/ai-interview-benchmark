# AI Interview Benchmark (AIB)

**A benchmark for evaluating answer-evaluation systems used in AI interviews.**

AIB does not rank job candidates. It ranks *evaluators*: the systems that score interview answers. An evaluator is good if it is stable, ranks better answers above worse ones, agrees with ground-truth scores, does not bias by difficulty, and grounds its feedback in evidence rather than filler.

## Status

- **Version:** 0.1.0-draft
- **Mode:** `OPEN_SUITE` (with a reserved `HIDDEN_HOLDOUT`)
- **Protocol:** MBP v0.1.0-draft
- **Dataset:** 24 cases (12 scoring, 6 ranking, 6 perturbation)

This is an MVP, not a frozen benchmark. It validates that MBP works in a second domain.

## Quick start

Python 3.11+; core code uses only the standard library.

```powershell
cd ai-interview-benchmark
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
aib validate
aib run --quick
```

## What is tested

AIB answers eight questions about an evaluator:

1. Same answer scored repeatedly — stable?
2. Better answer ranked above weaker answer?
3. Score grounded in actual evidence?
4. Does verbosity unfairly change score?
5. Does wording change score without factual change?
6. Does ASR-like noise destabilize score?
7. Does answer length create bias?
8. Does the evaluator systematically bias difficulty bands?

## Metrics

See [`METRICS.md`](METRICS.md). In summary: ranking consistency, MAE, stability sigma, level bias, evidence grounding, paraphrase score drift. No single composite score.

## Baselines

See [`BASELINES.md`](BASELINES.md). Three simple reference evaluators: length-based, keyword-based, constant.

## Adapter contract

An evaluator is a callable `(question, answer) -> {score, feedback, cited_evidence}`. See [`examples/echo_evaluator.py`](examples/echo_evaluator.py).

## Why this exists

The product evaluator at `washine/washine-personal-ai/ai_engine/prompts/evaluator.v2.yaml` names these metrics (ranking consistency, MAE, stability sigma, level bias, evidence grounding) but implements them as a prompt, not as standalone testable code. AIB extracts those metric names into a reproducible, CI-gated benchmark so evaluator quality is measured, not assumed.

## License

[Apache-2.0](LICENSE).
