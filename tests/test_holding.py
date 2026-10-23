"""Tests for the Holding class: gain/loss calculations and input validation."""

from dataclasses import FrozenInstanceError

import pytest

from portfolio_tracker.holding import AssetType, Holding


def make_holding(**overrides: object) -> Holding:
    """Build a valid RY holding, replacing any fields given in overrides."""
    fields: dict[str, object] = {
        "ticker": "RY",
        "name": "Royal Bank of Canada",
        "asset_type": AssetType.STOCK,
        "sector": "Financials",
        "quantity": 500,
        "average_cost": 120.00,
        "current_price": 135.00,
    }
    fields.update(overrides)
    return Holding(**fields)


# --- Calculations -----------------------------------------------------------


def test_cost_basis_is_quantity_times_average_cost() -> None:
    assert make_holding().cost_basis == 60_000


def test_market_value_is_quantity_times_current_price() -> None:
    assert make_holding().market_value == 67_500


def test_gain_loss_is_market_value_minus_cost_basis() -> None:
    assert make_holding().gain_loss == 7_500


def test_gain_loss_pct_is_gain_loss_divided_by_cost_basis() -> None:
    assert make_holding().gain_loss_pct == pytest.approx(0.125)


def test_losing_position_has_negative_gain_loss() -> None:
    holding = make_holding(current_price=96.00)

    assert holding.gain_loss == -12_000
    assert holding.gain_loss_pct == pytest.approx(-0.20)


def test_fractional_quantity_is_allowed() -> None:
    assert make_holding(quantity=2.5).market_value == pytest.approx(337.50)


def test_holding_cannot_be_changed_after_creation() -> None:
    holding = make_holding()

    with pytest.raises(FrozenInstanceError):
        holding.quantity = 1  # type: ignore[misc]


# --- Validation -------------------------------------------------------------


@pytest.mark.parametrize("field", ["ticker", "name", "sector"])
@pytest.mark.parametrize("blank", ["", "   "])
def test_blank_text_fields_are_rejected(field: str, blank: str) -> None:
    with pytest.raises(ValueError, match=f"{field} must not be empty"):
        make_holding(**{field: blank})


@pytest.mark.parametrize("quantity", [0, -10])
def test_zero_or_negative_quantity_is_rejected(quantity: float) -> None:
    with pytest.raises(ValueError, match="quantity must be greater than 0"):
        make_holding(quantity=quantity)


@pytest.mark.parametrize("field", ["average_cost", "current_price"])
@pytest.mark.parametrize("price", [0, -1.50])
def test_zero_or_negative_prices_are_rejected(field: str, price: float) -> None:
    with pytest.raises(ValueError, match=f"{field} must be greater than 0"):
        make_holding(**{field: price})


def test_number_given_as_text_is_rejected() -> None:
    with pytest.raises(TypeError, match="quantity must be a number"):
        make_holding(quantity="500")


def test_asset_type_given_as_plain_text_is_rejected() -> None:
    with pytest.raises(TypeError, match="asset_type must be an AssetType"):
        make_holding(asset_type="STOCK")
