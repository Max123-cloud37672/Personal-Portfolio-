"""Smoke test: checks the project is set up so tests can import our package."""


def test_portfolio_tracker_package_can_be_imported() -> None:
    import portfolio_tracker

    assert portfolio_tracker.__name__ == "portfolio_tracker"
