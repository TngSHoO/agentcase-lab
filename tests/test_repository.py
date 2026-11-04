from pathlib import Path

from agentcase.repository import ensure_database, get_case, get_cases, get_steps


def test_repository_seeds_and_reads_demo_data(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("AGENTCASE_DB_PATH", str(db_path))

    assert ensure_database() == db_path
    cases = get_cases()
    assert len(cases) == 30
    case = get_case(cases[0]["id"])
    assert case is not None
    assert len(get_steps(case["id"])) == 6
