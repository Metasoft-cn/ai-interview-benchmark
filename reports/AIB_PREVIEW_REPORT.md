# AIB v0.2 Preview Report

**Status:** PREVIEW (frozen)
**Dataset hash:** `a2262192276a915bbf19c0967f1a64bcdc4a8ebd0542424dab72e6792e5dc0bf`
**Total cases:** 108 (24 curated + 60 generated + 24 invariance)

## Dataset Splits

| Split | Cases | Released |
|-------|-------|----------|
| train | 8 | Yes |
| dev | 16 | Yes |
| public_test | 30 | Yes |
| hidden_test | 30 | **No** |

## Perturbation Coverage

| Type | Count |
|------|-------|
| asr_noise | 12 |
| paraphrase | 24 |
| verbosity | 24 |

## Invariance Test

Groups: 6
Cases: 24

### Baseline Invariance Results

| Baseline | Pass Rate | Mean Drift | Max Drift | Failed Groups |
|----------|-----------|-----------|-----------|---------------|
| length | 100.0% | 0.00 | 0.00 | 0 |
| keyword | 100.0% | 0.00 | 0.00 | 0 |
| constant | 100.0% | 0.00 | 0.00 | 0 |

## Metrics

1. ranking_consistency — fraction of ranking cases correct
2. mae — mean absolute error
3. stability_sigma — mean per-case stdev
4. level_bias — per-difficulty signed error
5. evidence_grounding — mean evidence recall
6. paraphrase_score_drift — mean perturbation drift

## Hidden Holdout

- Cases: 30
- SHA256: `37ce722e7e3296353657c2eef68ab4220dc4c8eeeb72775fab564b06f9f71d56`
- Released: **No** (MBP Verified Score only)

## Methodology

This benchmark follows the MBP evaluation methodology:
1. **Dataset split** — train/dev/public_test/hidden_test prevents overfitting
2. **Perturbation generator** — paraphrase/verbosity/asr_noise test semantic understanding
3. **Invariance test** — same capability, different expression → scores should be close
4. **Hidden holdout** — MBP Public Score vs MBP Verified Score
