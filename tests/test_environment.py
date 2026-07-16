from gks_tutorial.environment import diagnostics


def test_diagnostics_always_reports_python() -> None:
    result = diagnostics()
    assert result["python"]
    assert "pydantic" in result
