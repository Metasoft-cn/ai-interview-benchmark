"""Perturbation generator for AIB v0.2.

Generates perturbations that preserve semantic intent while varying surface
form. Three perturbation types:

- paraphrase: rephrase question/answer keeping meaning
- verbosity: expand or compress answer keeping key evidence
- asr_noise: inject ASR recognition errors

All generation is deterministic (fixed seed, template-based, no LLM calls).
Every generated case is labeled: curated / template-derived / synthetic.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any


@dataclass
class PerturbationConfig:
    seed: int = 20260927
    paraphrase_per_base: int = 2
    verbosity_per_base: int = 2
    asr_noise_per_base: int = 1


QUESTION_PARAPHRASES: dict[str, list[str]] = {
    "请用一分钟介绍你自己": [
        "做个自我介绍吧",
        "能简单介绍一下你的背景吗",
        "让我了解一下你是谁",
    ],
    "你为什么申请这个岗位": [
        "你为什么想来我们公司",
        "是什么吸引你投递这个职位",
        "谈谈你选择这个岗位的原因",
    ],
    "描述一个你解决过的技术难题": [
        "说一个你遇到过的技术挑战",
        "分享一个你解决的技术问题",
        "讲讲你克服过的技术困难",
    ],
    "你如何处理团队中的意见冲突": [
        "团队有分歧时你怎么做",
        "同事意见不合时你怎么办",
        "说说你处理团队分歧的方式",
    ],
    "请设计一个支持百万并发的订单系统": [
        "如果要设计百万并发订单系统你会怎么做",
        "百万并发订单系统怎么设计",
        "给我一个百万并发订单系统的设计方案",
    ],
    "谈谈你最大的失败和收获": [
        "说说你最大的挫折和学到的东西",
        "分享一次失败经历和你的成长",
        "你最惨痛的教训是什么",
    ],
}

ASR_NOISE_MAP: dict[str, str] = {
    "的": "得",
    "了": "勒",
    "是": "使",
    "在": "再",
    "和": "合",
    "我": "沃",
    "你": "尼",
    "他": "塌",
    "这": "者",
    "到": "道",
}

FILLER_SOUNDS = ["嗯", "啊", "那个", "就是", "然后"]


def _stable_id(base_id: str, ptype: str, variant: int) -> str:
    return f"pt_{base_id}_{ptype}_{variant:03d}"


def paraphrase_case(base: dict[str, Any], variant: int, rng: random.Random) -> dict[str, Any]:
    q = base["question"]
    paraphrases = QUESTION_PARAPHRASES.get(q, [])
    if not paraphrases:
        return None
    idx = variant % len(paraphrases)
    new_q = paraphrases[idx]

    answer = base["answer"]
    connectors = ["", "，", "，"]
    parts = answer.replace("，", " ").replace("。", " ").split()
    if len(parts) > 1:
        rng.shuffle(parts)
        new_a = "，".join(parts) + "。"
    else:
        new_a = answer

    return {
        "case_id": _stable_id(base["case_id"], "paraphrase", variant),
        "type": "perturbation",
        "base_case_id": base["case_id"],
        "perturbation": "paraphrase",
        "label": "template-derived",
        "question": new_q,
        "answer": new_a,
        "expected_score": base["ground_truth_score"],
    }


def verbosity_case(base: dict[str, Any], variant: int, rng: random.Random) -> dict[str, Any]:
    answer = base["answer"]
    if variant % 2 == 0:
        commas = answer.replace("，", " ").replace("。", " ").split()
        if len(commas) > 2:
            kept = commas[: len(commas) // 2 + 1]
            new_a = "，".join(kept) + "。"
        else:
            new_a = answer
    else:
        filler = rng.choice(FILLER_SOUNDS)
        new_a = f"{filler}，{answer}"

    return {
        "case_id": _stable_id(base["case_id"], "verbosity", variant),
        "type": "perturbation",
        "base_case_id": base["case_id"],
        "perturbation": "verbosity",
        "label": "template-derived",
        "question": base["question"],
        "answer": new_a,
        "expected_score": base["ground_truth_score"],
    }


def asr_noise_case(base: dict[str, Any], variant: int, rng: random.Random) -> dict[str, Any]:
    answer = base["answer"]
    chars = list(answer)
    positions = rng.sample(range(len(chars)), min(3, len(chars)))
    for pos in positions:
        ch = chars[pos]
        if ch in ASR_NOISE_MAP:
            chars[pos] = ASR_NOISE_MAP[ch]
        elif ch == "，" and rng.random() < 0.3:
            chars[pos] = ""
    new_a = "".join(chars)

    return {
        "case_id": _stable_id(base["case_id"], "asr_noise", variant),
        "type": "perturbation",
        "base_case_id": base["case_id"],
        "perturbation": "asr_noise",
        "label": "synthetic",
        "question": base["question"],
        "answer": new_a,
        "expected_score": base["ground_truth_score"],
    }


def generate_perturbations(
    base_cases: list[dict[str, Any]],
    config: PerturbationConfig | None = None,
) -> list[dict[str, Any]]:
    config = config or PerturbationConfig()
    rng = random.Random(config.seed)
    results: list[dict[str, Any]] = []

    for base in base_cases:
        if base.get("type") != "scoring":
            continue
        for v in range(config.paraphrase_per_base):
            case = paraphrase_case(base, v, rng)
            if case:
                results.append(case)
        for v in range(config.verbosity_per_base):
            results.append(verbosity_case(base, v, rng))
        for v in range(config.asr_noise_per_base):
            results.append(asr_noise_case(base, v, rng))

    return results


def write_jsonl(cases: list[dict[str, Any]], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for case in cases:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
