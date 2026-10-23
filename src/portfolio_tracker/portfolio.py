"""A client's portfolio: all their holdings, with totals and allocation."""

from dataclasses import dataclass

import pandas as pd

from portfolio_tracker.holding import Holding
from portfolio_tracker.validation import require_text


@dataclass(frozen=True)
class Portfolio:
    """All holdings for one fictional client. All amounts are in CAD."""

    client_name: str
    holdings: tuple[Holding, ...]

    def __post_init__(self) -> None:
        """Reject invalid inputs as soon as a portfolio is created."""
        require_text("client_name", self.client_name)

        if not self.holdings:
            raise ValueError("a portfolio must contain at least one holding")

        for holding in self.holdings:
            if not isinstance(holding, Holding):
                raise TypeError(
                    f"holdings must contain Holding objects, got {holding!r}"
                )

        _reject_duplicate_tickers(self.holdings)

    @property
    def total_cost_basis(self) -> float:
        """Total amount invested across all holdings."""
        return sum(holding.cost_basis for holding in self.holdings)

    @property
    def total_market_value(self) -> float:
        """What the whole portfolio is worth today."""
        return sum(holding.market_value for holding in self.holdings)

    @property
    def total_gain_loss(self) -> float:
        """Unrealized profit (positive) or loss (negative) in dollars."""
        return self.total_market_value - self.total_cost_basis

    @property
    def total_gain_loss_pct(self) -> float:
        """Gain or loss as a fraction of the amount invested."""
        return self.total_gain_loss / self.total_cost_basis

    @property
    def number_of_holdings(self) -> int:
        """How many positions the client holds."""
        return len(self.holdings)

    def weights(self) -> dict[str, float]:
        """Each holding's share of total market value, keyed by ticker."""
        return {holding.ticker: self._weight(holding) for holding in self.holdings}

    def allocation_by_sector(self) -> dict[str, float]:
        """Share of total market value in each sector, largest first."""
        return self._allocation_by("Sector")

    def allocation_by_asset_type(self) -> dict[str, float]:
        """Share of total market value in stocks vs ETFs, largest first."""
        return self._allocation_by("Type")

    def to_dataframe(self) -> pd.DataFrame:
        """One row per holding, largest market value first, ready to display."""
        rows = [
            {
                "Ticker": holding.ticker,
                "Name": holding.name,
                "Type": holding.asset_type.value,
                "Sector": holding.sector,
                "Quantity": holding.quantity,
                "Average Cost": holding.average_cost,
                "Current Price": holding.current_price,
                "Cost Basis": holding.cost_basis,
                "Market Value": holding.market_value,
                "Gain/Loss": holding.gain_loss,
                "Gain/Loss %": holding.gain_loss_pct,
                "Weight": self._weight(holding),
            }
            for holding in self.holdings
        ]
        table = pd.DataFrame(rows)
        return table.sort_values("Market Value", ascending=False, ignore_index=True)

    def _weight(self, holding: Holding) -> float:
        """One holding's market value as a fraction of the portfolio's."""
        return holding.market_value / self.total_market_value

    def _allocation_by(self, column: str) -> dict[str, float]:
        """Add up holding weights within each group of the given column."""
        weights = self.to_dataframe().groupby(column)["Weight"].sum()
        return weights.sort_values(ascending=False).to_dict()


def _reject_duplicate_tickers(holdings: tuple[Holding, ...]) -> None:
    """Raise an error if the same ticker appears more than once."""
    tickers = [holding.ticker for holding in holdings]
    duplicates = sorted({ticker for ticker in tickers if tickers.count(ticker) > 1})
    if duplicates:
        raise ValueError(f"duplicate tickers: {', '.join(duplicates)}")
