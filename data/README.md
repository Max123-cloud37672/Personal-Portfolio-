# Sample data (illustrative only)

All clients are fictional and every price and cost is made up. The tickers are
real Canadian listings, used only so the example looks familiar. Nothing here is
real market data, real client information or a recommendation.

| File | One row per | Columns |
|---|---|---|
| `prices.csv` | security | ticker, name, asset_type (`Stock` or `ETF`), sector, current_price |
| `holdings.csv` | client position | client, ticker, quantity, average_cost |

Every ticker in `holdings.csv` must appear in `prices.csv`. All amounts are CAD.
