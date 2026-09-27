"""Reference baseline evaluators.

Baselines are intentionally simple reference algorithms for sanity and comparison,
not weak fake competitors (per MBP separation-of-concerns).
"""


def length_baseline(question, answer):
    """Score by answer length. A naive reference."""
    score = min(100.0, len(answer) * 2.0)
    return {"score": score, "feedback": "length-based", "cited_evidence": []}


def keyword_baseline(question, answer):
    """Score by presence of reasoning-indicating keywords."""
    keywords = [
        "因为", "所以", "例如", "首先", "其次", "数据", "经验", "项目", "结果",
        "because", "for example", "first", "second", "data", "result",
    ]
    low = answer.lower()
    hits = sum(1 for k in keywords if k in low)
    score = min(100.0, hits * 18.0)
    return {"score": score, "feedback": f"keyword hits: {hits}", "cited_evidence": []}


def constant_baseline(question, answer):
    """A constant-score sanity baseline."""
    return {"score": 50.0, "feedback": "constant", "cited_evidence": []}


BASELINES = {
    "length": length_baseline,
    "keyword": keyword_baseline,
    "constant": constant_baseline,
}
