from agentcase.metrics import cause_distribution, model_performance, overview_metrics
from agentcase.seed import build_demo_dataset


def _case_dicts():
    cases, _ = build_demo_dataset()
    return [case.model_dump() for case in cases]


def test_overview_metrics_are_in_valid_ranges() -> None:
    metrics = overview_metrics(_case_dicts())
    assert metrics["total"] == 30
    assert 0 < metrics["success_rate"] < 1
    assert metrics["avg_latency_ms"] > 0
    assert metrics["avg_cost"] > 0
    assert metrics["repair_rate"] == 1


def test_distributions_are_populated() -> None:
    cases = _case_dicts()
    assert sum(item["案例数"] for item in cause_distribution(cases)) == sum(
        case["status"] == "failed" for case in cases
    )
    assert len(model_performance(cases)) == 4
