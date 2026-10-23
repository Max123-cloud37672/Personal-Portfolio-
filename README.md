# HNW Portfolio Tracker

[![CI](https://github.com/Max123-cloud37672/Personal-Portfolio-/actions/workflows/ci.yml/badge.svg)](https://github.com/Max123-cloud37672/Personal-Portfolio-/actions/workflows/ci.yml)

A portfolio tracker for high-net-worth (HNW) clients, built in Python. An advisor
picks a client and sees what they hold, what it is worth, how much it has gained
or lost, and how the portfolio is allocated.

> **Illustrative data only.** All clients are fictional and all prices are made up.
> Nothing in this project is real client information, real market data or real
> investment performance.

## Status

Work in progress, built milestone by milestone with tests at every step.

| Milestone | Status |
|---|---|
| Project setup (virtual environment, pinned dependencies, pytest, Ruff) | Done |
| `Holding` class: cost basis, market value, gain/loss, input validation | Done |
| Continuous integration (GitHub Actions runs Ruff and pytest on every PR) | Done |
| `Portfolio` class: totals, weights, allocation by holding and sector | Planned |
| CSV loader and sample data for several fictional clients | Planned |
| Streamlit dashboard: client selector, totals, holdings table, allocation chart | Planned |

## Key calculations

For one holding (for example 500 shares bought at an average of $120, now $135):

| Measure | Formula | Example |
|---|---|---|
| Cost basis (amount invested) | quantity × average cost | 500 × $120 = $60,000 |
| Market value | quantity × current price | 500 × $135 = $67,500 |
| Gain/loss ($) | market value − cost basis | +$7,500 |
| Gain/loss (%) | gain/loss ÷ cost basis | +12.5% |

Invalid inputs (blank names, zero or negative quantities or prices, wrong types)
are rejected with a clear error as soon as a holding is created. Because cost
basis is always positive, the percentage calculation can never divide by zero.

## Assumptions

- Canadian-listed stocks and ETFs, all amounts in CAD.
- Prices are entered from a file, not fetched live.
- Gain/loss is unrealized: no sales, dividends or fees are modelled.

## Tech stack

Python 3.14 · pandas · NumPy · Streamlit · Plotly · pytest · Ruff · GitHub Actions

## Running the tests

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
ruff check .
```

## Project structure

```
src/portfolio_tracker/   calculation code (no dashboard logic)
tests/                   pytest test suite
.github/workflows/       CI configuration
```

## How this was built

This is a learning project. I used Claude (Anthropic) as a coding tutor: I
directed the design decisions, reviewed every change, ran the tests and wrote
every commit myself.
