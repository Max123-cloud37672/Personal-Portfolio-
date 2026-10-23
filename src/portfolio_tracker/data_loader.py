"""Load illustrative client portfolios from two CSV files.

prices.csv   one row per security: ticker, name, asset_type, sector, current_price
holdings.csv one row per position: client, ticker, quantity, average_cost

Keeping prices in their own file means each security has exactly one price,
shared by every client who holds it.
"""

import csv
import math
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from portfolio_tracker.holding import AssetType, Holding
from portfolio_tracker.portfolio import Portfolio
from portfolio_tracker.validation import require_positive_number

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

PRICE_COLUMNS = ("ticker", "name", "asset_type", "sector", "current_price")
HOLDING_COLUMNS = ("client", "ticker", "quantity", "average_cost")


class DataError(ValueError):
    """A data file is missing columns or contains an invalid value."""


@dataclass(frozen=True)
class _Security:
    """One row of prices.csv, after its values have been checked."""

    name: str
    asset_type: AssetType
    sector: str
    current_price: float


def load_sample_portfolios() -> dict[str, Portfolio]:
    """Load the illustrative clients shipped in the project's data/ folder."""
    return load_portfolios(DATA_DIR / "holdings.csv", DATA_DIR / "prices.csv")


def load_portfolios(holdings_path: Path, prices_path: Path) -> dict[str, Portfolio]:
    """Build one Portfolio per client, pricing every holding from prices_path."""
    securities = _load_securities(prices_path)
    holdings_by_client: dict[str, list[Holding]] = {}

    for where, row in _read_rows(holdings_path, HOLDING_COLUMNS):
        with _report_errors_at(where):
            client = _parse_text("client", row["client"])
            ticker = _parse_text("ticker", row["ticker"])
            if ticker not in securities:
                raise ValueError(f"ticker {ticker} has no price in {prices_path.name}")
            security = securities[ticker]
            holding = Holding(
                ticker=ticker,
                name=security.name,
                asset_type=security.asset_type,
                sector=security.sector,
                quantity=_parse_number("quantity", row["quantity"]),
                average_cost=_parse_number("average_cost", row["average_cost"]),
                current_price=security.current_price,
            )
        holdings_by_client.setdefault(client, []).append(holding)

    portfolios: dict[str, Portfolio] = {}
    for client, holdings in holdings_by_client.items():
        with _report_errors_at(holdings_path.name):
            portfolios[client] = Portfolio(client_name=client, holdings=tuple(holdings))
    return portfolios


def _load_securities(prices_path: Path) -> dict[str, _Security]:
    """Read prices.csv into a lookup table keyed by ticker."""
    securities: dict[str, _Security] = {}

    for where, row in _read_rows(prices_path, PRICE_COLUMNS):
        with _report_errors_at(where):
            ticker = _parse_text("ticker", row["ticker"])
            if ticker in securities:
                raise ValueError(f"duplicate ticker {ticker}")
            current_price = _parse_number("current_price", row["current_price"])
            require_positive_number("current_price", current_price)
            securities[ticker] = _Security(
                name=_parse_text("name", row["name"]),
                asset_type=_parse_asset_type(row["asset_type"]),
                sector=_parse_text("sector", row["sector"]),
                current_price=current_price,
            )
    return securities


def _read_rows(
    path: Path, required_columns: tuple[str, ...]
) -> list[tuple[str, dict[str, str]]]:
    """Return (location, row) pairs, e.g. ("holdings.csv line 2", {...})."""
    # utf-8-sig also accepts files saved by Excel, which start with a hidden marker.
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, restval="")
        columns = reader.fieldnames or []
        missing = [column for column in required_columns if column not in columns]
        if missing:
            raise DataError(f"{path.name} is missing columns: {', '.join(missing)}")
        # Line 1 is the header, so the first data row is line 2.
        return [
            (f"{path.name} line {line}", row)
            for line, row in enumerate(reader, start=2)
        ]


@contextmanager
def _report_errors_at(where: str) -> Iterator[None]:
    """Turn any validation error inside the block into a DataError naming where."""
    try:
        yield
    except (TypeError, ValueError) as error:
        raise DataError(f"{where}: {error}") from error


def _parse_text(column: str, text: str) -> str:
    """Return the text without surrounding spaces, rejecting empty cells."""
    if not text.strip():
        raise ValueError(f"{column} is empty")
    return text.strip()


def _parse_number(column: str, text: str) -> float:
    """Convert a cell to a number, rejecting empty cells, text and 'nan'."""
    if not text.strip():
        raise ValueError(f"{column} is empty")
    try:
        number = float(text)
    except ValueError:
        number = math.nan
    if not math.isfinite(number):
        raise ValueError(f"{column} must be a number, got {text!r}")
    return number


def _parse_asset_type(text: str) -> AssetType:
    """Convert a cell such as 'Stock' or 'ETF' to an AssetType."""
    try:
        return AssetType(text.strip())
    except ValueError:
        allowed = ", ".join(asset_type.value for asset_type in AssetType)
        raise ValueError(
            f"asset_type must be one of: {allowed}, got {text!r}"
        ) from None
