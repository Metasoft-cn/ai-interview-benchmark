# AI Interview Benchmark — Baselines

Baselines are intentionally simple reference evaluators for sanity and comparison, not weak fake competitors (per MBP separation-of-concerns).

## length

`score = min(100, len(answer) * 2)`

Scores by answer length. A long answer is not necessarily a good answer, so this baseline is expected to have poor ranking consistency and high paraphrase drift on verbosity perturbations. It exists to show what a naive evaluator gets wrong.

## keyword

`score = min(100, keyword_hits * 18)` where keywords are reasoning indicators (`因为`, `所以`, `例如`, `首先`, `数据`, `项目`, `because`, `for example`, ...).

Scores by presence of reasoning-indicating terms. Better than length at ranking, but blind to content correctness and evidence grounding.

## constant

`score = 50`

A constant score. Ranking consistency is 0 (never orders), stability sigma is 0 (perfectly deterministic), MAE depends on ground-truth distribution. A sanity floor.
