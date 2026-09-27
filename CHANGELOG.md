# Changelog

## 0.1.0-draft — 2026-09-27

### Added
- Initial AI Interview Benchmark MVP: 24 cases (12 scoring, 6 ranking, 6 perturbation).
- Six metrics: ranking consistency, MAE, stability sigma, level bias, evidence grounding, paraphrase score drift.
- Three baselines: length, keyword, constant.
- Adapter contract and echo example.
- MBP v0.1.0-draft conformance: benchmark-manifest.json + dataset MANIFEST.json.
- CI: Ubuntu/Windows × Python 3.11/3.12.
- Metric unit tests and invariance tests.

### Sources
- Metric names reused from `washine/washine-personal-ai/ai_engine/prompts/evaluator.v2.yaml` (ranking consistency, MAE, stability sigma, level bias, evidence grounding), implemented here as standalone testable code.
