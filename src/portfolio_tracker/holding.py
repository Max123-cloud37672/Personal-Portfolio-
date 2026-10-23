"""A single position in a client's portfolio: what is held and what it is worth."""

from dataclasses import dataclass
from enum import Enum


class AssetType(Enum):
    """The kinds of investment the tracker supports."""

    STOCK = "Stock"
    ETF = "ETF"


@dataclass(frozen=True)
class Holding:
    """One position, e.g. 500 shares of RY bought at $120, now trading at $135.

    All amounts are in Canadian dollars (CAD). Prices are per share.
    """

    ticker: str
    name: str
    asset_type: AssetType
    sector: str
    quantity: float
    average_cost: float
    current_price: float

    def __post_init__(self) -> None:
        """Reject invalid inputs as soon as a holding is created."""
        for field_name in ("ticker", "name", "sector"):
            _require_text(field_name, getattr(self, field_name))

        if not isinstance(self.asset_type, AssetType):
            raise TypeError(
                f"asset_type must be an AssetType (e.g. AssetType.STOCK), "
                f"got {self.asset_type!r}"
            )

        for field_name in ("quantity", "average_cost", "current_price"):
            _require_positive_number(field_name, getattr(self, field_name))

    @property
    def cost_basis(self) -> float:
        """Total amount invested: quantity x average cost."""
        return self.quantity * self.average_cost

    @property
    def market_value(self) -> float:
        """What the position is worth today: quantity x current price."""
        return self.quantity * self.current_price

    @property
    def gain_loss(self) -> float:
        """Unrealized profit (positive) or loss (negative) in dollars."""
        return self.market_value - self.cost_basis

    @property
    def gain_loss_pct(self) -> float:
        """Gain or loss as a fraction of the amount invested (0.125 = 12.5%)."""
        return self.gain_loss / self.cost_basis


def _require_text(field_name: str, value: object) -> None:
    """Raise an error unless value is a non-blank string."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be text, got {value!r}")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _require_positive_number(field_name: str, value: object) -> None:
    """Raise an error unless value is a number greater than zero."""
    if not isinstance(value, int | float):
        raise TypeError(f"{field_name} must be a number, got {value!r}")
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than 0, got {value}")
