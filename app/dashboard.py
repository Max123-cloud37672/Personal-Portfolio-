"""Streamlit dashboard for the illustrative HNW portfolio tracker.

Run it with:  streamlit run app/dashboard.py

This file only displays results. Every calculation lives in portfolio_tracker.
"""

import plotly.graph_objects as go
import streamlit as st

from portfolio_tracker.data_loader import DataError, load_sample_portfolios
from portfolio_tracker.portfolio import Portfolio

BAR_COLOUR = "#2a78d6"

ILLUSTRATIVE_NOTICE = (
    "**Illustrative data.** All clients are fictional and all prices are made up. "
    "Nothing shown is real client information, market data or performance."
)


# --- Number formatting ------------------------------------------------------


def format_cad(amount: float) -> str:
    """Format a dollar amount, e.g. 2797400 -> '$2,797,400'."""
    return f"${amount:,.0f}"


def format_signed_cad(amount: float) -> str:
    """Format a gain or loss with its sign, e.g. 931850 -> '+$931,850'."""
    sign = "+" if amount >= 0 else "-"
    return f"{sign}${abs(amount):,.0f}"


def format_signed_pct(fraction: float) -> str:
    """Format a fraction as a signed percentage, e.g. 0.333 -> '+33.3%'."""
    return f"{fraction:+.1%}"


# --- Page sections ----------------------------------------------------------


@st.cache_data
def load_portfolios() -> dict[str, Portfolio]:
    """Load the sample clients once and reuse them while the app is running."""
    return load_sample_portfolios()


def show_headline_numbers(portfolio: Portfolio) -> None:
    """Four headline figures across the top of the page."""
    invested, value, gain, holdings = st.columns(4)
    invested.metric("Invested", format_cad(portfolio.total_cost_basis))
    value.metric("Market value", format_cad(portfolio.total_market_value))
    gain.metric(
        "Gain/loss",
        format_signed_cad(portfolio.total_gain_loss),
        delta=format_signed_pct(portfolio.total_gain_loss_pct),
    )
    holdings.metric("Holdings", portfolio.number_of_holdings)


def allocation_chart(weights: dict[str, float], category: str) -> go.Figure:
    """Horizontal bar chart of portfolio shares, largest at the top."""
    ranked = sorted(weights.items(), key=lambda item: item[1], reverse=True)
    labels = [label for label, _ in ranked]
    shares = [share for _, share in ranked]

    figure = go.Figure(
        go.Bar(
            x=shares,
            y=labels,
            orientation="h",
            marker={"color": BAR_COLOUR, "cornerradius": 4},
            text=[f"{share:.1%}" for share in shares],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"{category}: %{{y}}<br>Share: %{{x:.1%}}<extra></extra>",
        )
    )
    figure.update_layout(
        xaxis={
            "title": "Share of portfolio market value",
            "tickformat": ".0%",
            "range": [0, max(shares) * 1.15],
        },
        yaxis={"title": category, "autorange": "reversed"},
        height=120 + 36 * len(labels),
        margin={"l": 0, "r": 40, "t": 10, "b": 0},
        bargap=0.35,
        showlegend=False,
    )
    return figure


def show_allocation(portfolio: Portfolio) -> None:
    """Allocation charts by sector, holding and asset type, in tabs."""
    st.subheader("Allocation")
    by_sector, by_holding, by_type = st.tabs(
        ["By sector", "By holding", "By asset type"]
    )
    with by_sector:
        chart = allocation_chart(portfolio.allocation_by_sector(), "Sector")
        st.plotly_chart(chart, width="stretch")
    with by_holding:
        chart = allocation_chart(portfolio.weights(), "Holding")
        st.plotly_chart(chart, width="stretch")
    with by_type:
        chart = allocation_chart(portfolio.allocation_by_asset_type(), "Asset type")
        st.plotly_chart(chart, width="stretch")


def show_holdings_table(portfolio: Portfolio) -> None:
    """Every holding with its cost, value, gain/loss and weight."""
    st.subheader("Holdings")
    number = st.column_config.NumberColumn
    table = portfolio.to_dataframe()
    table[["Gain/Loss %", "Weight"]] *= 100  # fractions -> percentages for display
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_order=[
            "Ticker",
            "Name",
            "Sector",
            "Quantity",
            "Average Cost",
            "Current Price",
            "Cost Basis",
            "Market Value",
            "Gain/Loss",
            "Gain/Loss %",
            "Weight",
        ],
        column_config={
            "Quantity": number("Qty", format="localized"),
            "Average Cost": number("Avg cost", format="dollar"),
            "Current Price": number("Price", format="dollar"),
            "Cost Basis": number("Invested", format="$%,.0f"),
            "Market Value": number("Value", format="$%,.0f"),
            "Gain/Loss": number("Gain/loss ($)", format="%+,.0f"),
            "Gain/Loss %": number("Gain/loss", format="%+.1f%%"),
            "Weight": number("Weight", format="%.1f%%"),
        },
    )


# --- Page -------------------------------------------------------------------


def main() -> None:
    st.set_page_config(page_title="HNW Portfolio Tracker", layout="wide")

    try:
        portfolios = load_portfolios()
    except DataError as error:
        st.error(f"Could not load the sample data. {error}")
        st.stop()

    with st.sidebar:
        st.header("HNW Portfolio Tracker")
        client = st.selectbox("Client", list(portfolios))
        st.caption("All amounts in CAD. Prices are an illustrative snapshot.")

    portfolio = portfolios[client]
    st.title(client)
    st.info(ILLUSTRATIVE_NOTICE)
    show_headline_numbers(portfolio)
    show_allocation(portfolio)
    show_holdings_table(portfolio)


main()
