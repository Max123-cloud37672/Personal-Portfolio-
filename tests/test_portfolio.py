"""Tests for the Portfolio class: totals, weights, allocation and validation."""

import pytest

from portfolio_tracker.holding import AssetType, Holding
from portfolio_tracker.portfolio import Portfolio


def make_holding(
    ticker: str,
    sector: str,
    quantity: float,
    average_cost: float,
    current_price: float,
    asset_type: AssetType = AssetType.STOCK,
) -> Holding:
    """Build a holding, using the ticker as its name to keep tests short."""
    return Holding(
        ticker=ticker,
        name=ticker,
        asset_type=asset_type,
        sector=sector,
        quantity=quantity,
        average_cost=average_cost,
        current_price=current_price,
    )


HOLDINGS = (
    make_holding("RY", "Financials", 500, 120.00, 135.00),
    make_holding("TD", "Financials", 400, 80.00, 75.00),
    make_holding("ENB", "Energy", 1_000, 50.00, 52.50),
    make_holding("XIU", "Broad Market", 1_600, 30.00, 31.25, AssetType.ETF),
)


@pytest.fixture
def portfolio() -> Portfolio:
    return Portfolio(client_name="Client A", holdings=HOLDINGS)


# --- Totals -----------------------------------------------------------------


def test_total_cost_basis_sums_all_holdings(portfolio: Portfolio) -> None:
    assert portfolio.total_cost_basis == 190_000


def test_total_market_value_sums_all_holdings(portfolio: Portfolio) -> None:
    assert portfolio.total_market_value == 200_000


def test_total_gain_loss_is_value_minus_cost(portfolio: Portfolio) -> None:
    assert portfolio.total_gain_loss == 10_000


def test_total_gain_loss_pct_is_gain_divided_by_cost(portfolio: Portfolio) -> None:
    assert portfolio.total_gain_loss_pct == pytest.approx(10_000 / 190_000)


# --- Weights and allocation -------------------------------------------------


def test_weights_are_market_value_shares(portfolio: Portfolio) -> None:
    assert portfolio.weights() == pytest.approx(
        {"RY": 0.3375, "TD": 0.15, "ENB": 0.2625, "XIU": 0.25}
    )


def test_weights_add_up_to_one(portfolio: Portfolio) -> None:
    assert sum(portfolio.weights().values()) == pytest.approx(1.0)


def test_allocation_by_sector_groups_weights(portfolio: Portfolio) -> None:
    assert portfolio.allocation_by_sector() == pytest.approx(
        {"Financials": 0.4875, "Energy": 0.2625, "Broad Market": 0.25}
    )


def test_allocation_by_sector_is_largest_first(portfolio: Portfolio) -> None:
    sectors = list(portfolio.allocation_by_sector())

    assert sectors == ["Financials", "Energy", "Broad Market"]


def test_allocation_by_asset_type_groups_weights(portfolio: Portfolio) -> None:
    assert portfolio.allocation_by_asset_type() == pytest.approx(
        {"Stock": 0.75, "ETF": 0.25}
    )


# --- Table for the dashboard ------------------------------------------------


def test_to_dataframe_has_one_row_per_holding(portfolio: Portfolio) -> None:
    table = portfolio.to_dataframe()

    assert len(table) == 4
    assert list(table.columns) == [
        "Ticker",
        "Name",
        "Type",
        "Sector",
        "Quantity",
        "Average Cost",
        "Current Price",
        "Cost Basis",
        "Market Value",
        "Gain/Loss",
        "Gain/Loss %",
        "Weight",
    ]


def test_to_dataframe_is_sorted_by_market_value(portfolio: Portfolio) -> None:
    tickers = list(portfolio.to_dataframe()["Ticker"])

    assert tickers == ["RY", "ENB", "XIU", "TD"]


# --- Validation -------------------------------------------------------------


def test_blank_client_name_is_rejected() -> None:
    with pytest.raises(ValueError, match="client_name must not be empty"):
        Portfolio(client_name=" ", holdings=HOLDINGS)


def test_portfolio_without_holdings_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least one holding"):
        Portfolio(client_name="Client A", holdings=())


def test_duplicate_ticker_is_rejected() -> None:
    duplicated = (*HOLDINGS, make_holding("RY", "Financials", 10, 100.00, 100.00))

    with pytest.raises(ValueError, match="duplicate tickers: RY"):
        Portfolio(client_name="Client A", holdings=duplicated)


def test_non_holding_item_is_rejected() -> None:
    with pytest.raises(TypeError, match="holdings must contain Holding objects"):
        Portfolio(client_name="Client A", holdings=(*HOLDINGS, "RY"))
