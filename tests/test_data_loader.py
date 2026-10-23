"""Tests for loading client portfolios from the holdings and prices CSV files."""

from pathlib import Path

import pytest

from portfolio_tracker.data_loader import (
    DataError,
    load_portfolios,
    load_sample_portfolios,
)
from portfolio_tracker.holding import AssetType

PRICES = """ticker,name,asset_type,sector,current_price
RY,Royal Bank of Canada,Stock,Financials,135.00
XIU,iShares S&P/TSX 60 Index ETF,ETF,Broad Market,31.25
"""

HOLDINGS = """client,ticker,quantity,average_cost
Client A,RY,500,120.00
Client A,XIU,1600,30.00
Client B,RY,100,140.00
"""


def write_files(
    tmp_path: Path, holdings: str = HOLDINGS, prices: str = PRICES
) -> tuple[Path, Path]:
    """Save the given CSV text to temporary files and return their paths."""
    holdings_path = tmp_path / "holdings.csv"
    prices_path = tmp_path / "prices.csv"
    holdings_path.write_text(holdings)
    prices_path.write_text(prices)
    return holdings_path, prices_path


# --- Loading valid files ----------------------------------------------------


def test_loads_one_portfolio_per_client(tmp_path: Path) -> None:
    portfolios = load_portfolios(*write_files(tmp_path))

    assert list(portfolios) == ["Client A", "Client B"]
    assert portfolios["Client A"].number_of_holdings == 2
    assert portfolios["Client B"].number_of_holdings == 1


def test_holding_combines_both_files(tmp_path: Path) -> None:
    portfolios = load_portfolios(*write_files(tmp_path))
    royal_bank = portfolios["Client A"].holdings[0]

    assert royal_bank.name == "Royal Bank of Canada"
    assert royal_bank.asset_type is AssetType.STOCK
    assert royal_bank.sector == "Financials"
    assert royal_bank.quantity == 500
    assert royal_bank.average_cost == 120.00
    assert royal_bank.current_price == 135.00


def test_same_ticker_has_same_price_for_every_client(tmp_path: Path) -> None:
    portfolios = load_portfolios(*write_files(tmp_path))

    client_a_price = portfolios["Client A"].holdings[0].current_price
    client_b_price = portfolios["Client B"].holdings[0].current_price
    assert client_a_price == client_b_price == 135.00


# --- Problems in the files --------------------------------------------------


def test_missing_column_is_rejected(tmp_path: Path) -> None:
    holdings = "client,ticker,quantity\nClient A,RY,500\n"

    with pytest.raises(
        DataError, match="holdings.csv is missing columns: average_cost"
    ):
        load_portfolios(*write_files(tmp_path, holdings=holdings))


def test_ticker_without_a_price_is_rejected(tmp_path: Path) -> None:
    holdings = HOLDINGS + "Client B,XYZ,10,5.00\n"

    with pytest.raises(
        DataError, match="holdings.csv line 5: ticker XYZ has no price in prices.csv"
    ):
        load_portfolios(*write_files(tmp_path, holdings=holdings))


@pytest.mark.parametrize("bad_value", ["abc", "nan"])
def test_text_in_a_number_column_is_rejected(tmp_path: Path, bad_value: str) -> None:
    holdings = HOLDINGS.replace("Client A,XIU,1600", f"Client A,XIU,{bad_value}")

    with pytest.raises(
        DataError, match="holdings.csv line 3: quantity must be a number"
    ):
        load_portfolios(*write_files(tmp_path, holdings=holdings))


def test_empty_cell_is_rejected(tmp_path: Path) -> None:
    holdings = HOLDINGS.replace("Client A,XIU,1600", "Client A,XIU,")

    with pytest.raises(DataError, match="holdings.csv line 3: quantity is empty"):
        load_portfolios(*write_files(tmp_path, holdings=holdings))


def test_invalid_holding_value_reports_its_line(tmp_path: Path) -> None:
    holdings = HOLDINGS.replace("Client A,XIU,1600", "Client A,XIU,-5")

    with pytest.raises(
        DataError, match="holdings.csv line 3: quantity must be greater than 0"
    ):
        load_portfolios(*write_files(tmp_path, holdings=holdings))


def test_unknown_asset_type_is_rejected(tmp_path: Path) -> None:
    prices = PRICES.replace("ETF,Broad Market", "Bond,Broad Market")

    with pytest.raises(
        DataError, match="prices.csv line 3: asset_type must be one of: Stock, ETF"
    ):
        load_portfolios(*write_files(tmp_path, prices=prices))


def test_zero_price_is_rejected(tmp_path: Path) -> None:
    prices = PRICES.replace("135.00", "0")

    with pytest.raises(
        DataError, match="prices.csv line 2: current_price must be greater than 0"
    ):
        load_portfolios(*write_files(tmp_path, prices=prices))


def test_duplicate_ticker_in_prices_is_rejected(tmp_path: Path) -> None:
    prices = PRICES + "RY,Royal Bank of Canada,Stock,Financials,140.00\n"

    with pytest.raises(DataError, match="prices.csv line 4: duplicate ticker RY"):
        load_portfolios(*write_files(tmp_path, prices=prices))


def test_same_ticker_twice_for_one_client_is_rejected(tmp_path: Path) -> None:
    holdings = HOLDINGS + "Client A,RY,50,130.00\n"

    with pytest.raises(DataError, match="holdings.csv: duplicate tickers: RY"):
        load_portfolios(*write_files(tmp_path, holdings=holdings))


# --- The sample data shipped with the project -------------------------------


def test_sample_data_has_three_clients_with_at_least_eight_holdings() -> None:
    portfolios = load_sample_portfolios()

    assert len(portfolios) == 3
    for portfolio in portfolios.values():
        assert portfolio.number_of_holdings >= 8
