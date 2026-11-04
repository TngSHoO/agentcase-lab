from agentcase.seed import ROOT_CAUSES, build_demo_dataset


def test_demo_dataset_contains_30_unique_cases() -> None:
    cases, steps = build_demo_dataset()
    assert len(cases) == 30
    assert len({case.id for case in cases}) == 30
    assert len(steps) == 180


def test_demo_dataset_covers_all_failure_categories() -> None:
    cases, _ = build_demo_dataset()
    observed = {case.root_cause for case in cases if case.status == "failed"}
    assert set(ROOT_CAUSES).issubset(observed)
