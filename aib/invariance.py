"""Invariance evaluator for AIB v0.2.

The invariance test is the MBP signature feature. It defines groups of
questions that test the same capability with different surface expressions.
A robust evaluator should give similar scores for all variants. Large drift
indicates keyword matching, not understanding.

Invariance groups:
  - same capability, different question phrasings
  - same answer, same expected score
  - evaluator score drift should be small
"""
from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from typing import Any, Callable


INVARIANCE_GROUPS: list[dict[str, Any]] = [
    {
        "group_id": "inv_001",
        "capability": "self_introduction",
        "questions": [
            "请用一分钟介绍你自己",
            "做个自我介绍吧",
            "能简单介绍一下你的背景吗",
            "让我了解一下你是谁",
        ],
        "answer": "我是一名有五年经验的后端工程师，主要负责过电商订单和支付系统的设计与优化，熟悉Java和Go，曾在双11期间将订单接口响应时间从800毫秒降到200毫秒。",
        "expected_score": 84,
        "max_acceptable_drift": 15.0,
    },
    {
        "group_id": "inv_002",
        "capability": "motivation",
        "questions": [
            "你为什么申请这个岗位",
            "你为什么想来我们公司",
            "是什么吸引你投递这个职位",
            "谈谈你选择这个岗位的原因",
        ],
        "answer": "因为贵公司的技术栈和我的经验高度匹配，我在上一份工作中用Go构建了高并发网关，而贵岗位正好需要这方面的经验，同时我也看好贵公司在支付领域的长期发展。",
        "expected_score": 86,
        "max_acceptable_drift": 15.0,
    },
    {
        "group_id": "inv_003",
        "capability": "technical_problem_solving",
        "questions": [
            "描述一个你解决过的技术难题",
            "说一个你遇到过的技术挑战",
            "分享一个你解决的技术问题",
            "讲讲你克服过的技术困难",
        ],
        "answer": "去年我们的支付系统在高峰期出现数据库连接池耗尽，我首先通过监控定位到连接泄漏来自一个未关闭的事务，然后引入连接池监控告警，最后重构成短事务模式，上线后再未复现。",
        "expected_score": 90,
        "max_acceptable_drift": 15.0,
    },
    {
        "group_id": "inv_004",
        "capability": "conflict_resolution",
        "questions": [
            "你如何处理团队中的意见冲突",
            "团队有分歧时你怎么做",
            "同事意见不合时你怎么办",
            "说说你处理团队分歧的方式",
        ],
        "answer": "我会先让各方完整表达自己的方案和依据，然后基于数据和项目目标做客观对比，例如上次关于缓存选型Redis还是Memcached的分歧，我拉了一个会用性能数据说话，最终选了Redis并记录了决策原因。",
        "expected_score": 83,
        "max_acceptable_drift": 15.0,
    },
    {
        "group_id": "inv_005",
        "capability": "system_design",
        "questions": [
            "请设计一个支持百万并发的订单系统",
            "如果要设计百万并发订单系统你会怎么做",
            "百万并发订单系统怎么设计",
            "给我一个百万并发订单系统的设计方案",
        ],
        "answer": "我会分层设计：接入层用网关做限流和熔断，服务层按订单状态拆分有状态服务，存储层订单库按用户分库、热点订单走缓存，消息层用Kafka异步解耦下游，同时设计幂等令牌防止重复下单。",
        "expected_score": 92,
        "max_acceptable_drift": 15.0,
    },
    {
        "group_id": "inv_006",
        "capability": "failure_reflection",
        "questions": [
            "谈谈你最大的失败和收获",
            "说说你最大的挫折和学到的东西",
            "分享一次失败经历和你的成长",
            "你最惨痛的教训是什么",
        ],
        "answer": "我曾因为没做灰度发布导致一次全量故障，影响用户约十分钟，事后我推动了灰度发布流程落地，并把发布检查项固化进CI，从那以后团队再未发生同类事故。",
        "expected_score": 80,
        "max_acceptable_drift": 15.0,
    },
]


@dataclass
class InvarianceResult:
    group_id: str
    capability: str
    scores: list[float]
    drift: float
    stdev: float
    passed: bool
    max_acceptable_drift: float


def evaluate_invariance(
    adapter: Callable[[str, str], dict[str, Any]],
    groups: list[dict[str, Any]] | None = None,
) -> list[InvarianceResult]:
    """Run invariance test on an adapter.

    Args:
        adapter: a callable (question, answer) -> {score, ...}
        groups: invariance groups (default: INVARIANCE_GROUPS)

    Returns:
        list of InvarianceResult, one per group
    """
    groups = groups or INVARIANCE_GROUPS
    results: list[InvarianceResult] = []

    for g in groups:
        scores = []
        for q in g["questions"]:
            pred = adapter(q, g["answer"])
            scores.append(float(pred["score"]))

        drift = max(scores) - min(scores) if scores else 0.0
        stdev = statistics.stdev(scores) if len(scores) > 1 else 0.0
        threshold = g["max_acceptable_drift"]
        passed = drift <= threshold

        results.append(InvarianceResult(
            group_id=g["group_id"],
            capability=g["capability"],
            scores=scores,
            drift=drift,
            stdev=stdev,
            passed=passed,
            max_acceptable_drift=threshold,
        ))

    return results


def invariance_summary(results: list[InvarianceResult]) -> dict[str, Any]:
    """Summarize invariance results for the preview report."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    return {
        "total_groups": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total > 0 else 0.0,
        "mean_drift": statistics.mean(r.drift for r in results) if results else 0.0,
        "max_drift": max(r.drift for r in results) if results else 0.0,
        "mean_stdev": statistics.mean(r.stdev for r in results) if results else 0.0,
        "failures": [
            {
                "group_id": r.group_id,
                "capability": r.capability,
                "drift": r.drift,
                "threshold": r.max_acceptable_drift,
                "scores": r.scores,
            }
            for r in results if not r.passed
        ],
    }


def export_invariance_cases(path: str) -> None:
    """Export invariance groups as JSONL for the dataset."""
    with open(path, "w", encoding="utf-8") as f:
        for g in INVARIANCE_GROUPS:
            for i, q in enumerate(g["questions"]):
                case = {
                    "case_id": f"{g['group_id']}_q{i+1}",
                    "type": "invariance",
                    "group_id": g["group_id"],
                    "capability": g["capability"],
                    "question": q,
                    "answer": g["answer"],
                    "expected_score": g["expected_score"],
                    "variant_index": i,
                    "max_acceptable_drift": g["max_acceptable_drift"],
                }
                f.write(json.dumps(case, ensure_ascii=False) + "\n")
