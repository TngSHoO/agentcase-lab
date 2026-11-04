from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def overview_metrics(cases: list[dict[str, Any]]) -> dict[str, float]:
    if not cases:
        return {
            "total": 0,
            "success_rate": 0.0,
            "avg_latency_ms": 0.0,
            "avg_cost": 0.0,
            "repair_rate": 0.0,
        }
    total = len(cases)
    successes = sum(case["status"] == "success" for case in cases)
    failed_cases = [case for case in cases if case["status"] == "failed"]
    repaired = sum(case["after_status"] == "success" for case in failed_cases)
    return {
        "total": total,
        "success_rate": successes / total,
        "avg_latency_ms": sum(case["latency_ms"] for case in cases) / total,
        "avg_cost": sum(case["token_cost"] for case in cases) / total,
        "repair_rate": repaired / len(failed_cases) if failed_cases else 1.0,
    }


def cause_distribution(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter = Counter(case["root_cause"] for case in cases if case["status"] == "failed")
    return [{"根因": cause, "案例数": count} for cause, count in counter.most_common()]


def model_performance(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        grouped[case["model_name"]].append(case)
    rows = []
    for model, items in grouped.items():
        rows.append(
            {
                "模型": model,
                "任务数": len(items),
                "成功率": sum(item["status"] == "success" for item in items) / len(items),
                "平均耗时秒": sum(item["latency_ms"] for item in items) / len(items) / 1000,
                "平均成本": sum(item["token_cost"] for item in items) / len(items),
            }
        )
    return sorted(rows, key=lambda row: row["成功率"], reverse=True)
