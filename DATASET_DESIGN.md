# AI Interview Benchmark — Dataset Design

## v0.1.0-draft

24 cases, all authored (curated) or perturbation-derived from curated cases. No synthetic bulk generation yet.

### Scoring cases (12)

Six question pairs: a strong answer and a weak answer for each of six common interview questions, spanning three difficulty bands:

| Difficulty | Questions |
|---|---|
| easy | self-introduction, motivation |
| medium | technical problem solved, team conflict |
| hard | system design, biggest failure |

Each case carries `ground_truth_score` (0–100, human-authored) and `evidence` (the facts that justify the score).

### Ranking cases (6)

One per question: `(answer_better, answer_worse)`. The evaluator must score the better answer higher.

### Perturbation cases (6)

Derived from scoring cases by meaning-preserving perturbation:

| Perturbation | Count | What it tests |
|---|---|---|
| paraphrase | 3 | wording invariance |
| verbosity | 2 | length invariance |
| asr_noise | 1 | recognition-noise robustness |

Each carries `expected_score` equal to its base case's `ground_truth_score`. Drift from `expected_score` is a finding.

## Provenance

All cases are authored by one contributor. No external adjudication is claimed. No real candidate data is used.

## Target before preview freeze

- 100–300 curated cases.
- Programmatic perturbation generation (paraphrase, verbosity, ASR-noise) with explicit `curated` / `template-derived` / `synthetic` labels.
- A reserved `HIDDEN_HOLDOUT` (not used until frozen).

## Manifest

`datasets/MANIFEST.json` records version, seed, generator, per-file hashes, counts, and a top-level digest. `aib validate` checks the manifest count matches the actual files.
