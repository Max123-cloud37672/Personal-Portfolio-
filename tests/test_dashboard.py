"""Tests for the Streamlit dashboard, run without a browser using AppTest."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

DASHBOARD = Path(__file__).resolve().parents[1] / "app" / "dashboard.py"


@pytest.fixture
def app() -> AppTest:
    """Run the dashboard once, as a fresh visitor would see it."""
    return AppTest.from_file(str(DASHBOARD)).run()


def metric_value(app: AppTest, label: str) -> str:
    """Return the displayed value of the headline number with this label."""
    return next(metric.value for metric in app.metric if metric.label == label)


def test_dashboard_runs_without_errors(app: AppTest) -> None:
    assert not app.exception


def test_illustrative_data_notice_is_shown(app: AppTest) -> None:
    assert any("Illustrative data" in notice.value for notice in app.info)


def test_first_client_is_shown_by_default(app: AppTest) -> None:
    assert app.title[0].value == "Client A (Growth)"


def test_headline_numbers_use_cad_formatting(app: AppTest) -> None:
    assert metric_value(app, "Invested") == "$2,797,400"
    assert metric_value(app, "Market value") == "$3,729,250"
    assert metric_value(app, "Gain/loss") == "+$931,850"


def test_holdings_count_is_shown(app: AppTest) -> None:
    assert metric_value(app, "Holdings") == "9"


def test_choosing_another_client_updates_the_page(app: AppTest) -> None:
    app.selectbox[0].select("Client B (Income)").run()

    assert app.title[0].value == "Client B (Income)"
    assert metric_value(app, "Market value") == "$6,139,400"


def test_holdings_table_has_one_row_per_holding(app: AppTest) -> None:
    assert len(app.dataframe[0].value) == 9
