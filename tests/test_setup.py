"""Smoke test: checks the project is set up so tests can import our package."""


def test_fixed_income_package_can_be_imported() -> None:
    import fixed_income

    assert fixed_income.__name__ == "fixed_income"
