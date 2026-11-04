from agentcase.analyzer import analyze_locally
from agentcase.seed import build_demo_dataset


def test_local_analyzer_returns_traceable_report() -> None:
    cases, steps = build_demo_dataset()
    failed_case = next(case for case in cases if case.status == "failed")
    related_steps = [step.model_dump() for step in steps if step.case_id == failed_case.id]
    report = analyze_locally(failed_case.model_dump(), related_steps)

    assert report.root_cause == failed_case.root_cause
    assert report.failed_step != "无"
    assert report.evidence
    assert report.recommendations
    assert report.source == "demo"
