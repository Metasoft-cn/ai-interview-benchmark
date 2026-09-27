# Changelog

## 0.2.0-preview.1 — 2026-09-27

### Added
- **Dataset split**: train (8) / dev (16) / public_test (30) / hidden_test (30, not released).
- **Perturbation generator** (`aib/perturbation.py`): paraphrase, verbosity, asr_noise. 60 generated cases labeled `template-derived` / `synthetic`. Deterministic (fixed seed, no LLM).
- **Invariance evaluator** (`aib/invariance.py`): 6 invariance groups (24 cases). Same capability, different question phrasings → scores should be close. MBP signature feature.
- **Hidden holdout**: `hidden/HOLDOUT_MANIFEST.json` with SHA256 + case count. Hidden test cases not released.
- **v0.2 manifest**: `benchmark-manifest-v0.2.json` with split metadata, perturbation coverage, invariance stats.
- **Preview report**: `reports/AIB_PREVIEW_REPORT.md` with dataset statistics, perturbation coverage, invariance results, hidden holdout status.
- 18 new tests (perturbation generator, invariance evaluator, dataset split). 34 tests total, all passing.
- `generate_v02_preview.py` script to regenerate all v0.2 artifacts.

### Changed
- Version bumped to 0.2.0.dev1 (pyproject.toml).
- `.gitignore` updated to exclude `datasets/splits/hidden_test.jsonl` and `hidden/hidden_test.jsonl`.

### Methodology
This release establishes the MBP evaluation methodology: dataset split prevents overfitting, perturbation generator tests semantic understanding, invariance test detects keyword matching, hidden holdout enables MBP Verified Score.

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
