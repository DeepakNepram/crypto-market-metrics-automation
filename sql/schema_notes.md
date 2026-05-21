## Database Schema

### crypto_timeseries
Full historical metrics for all coins.
| Column | Type | Description |
|--------|------|-------------|
| timestamp | DATETIME | UTC date of the data point |
| coin_id | VARCHAR | CoinGecko coin identifier (e.g., 'bitcoin') |
| symbol | VARCHAR | Ticker symbol (e.g., 'BTC') |
| vs_currency | VARCHAR | Quote currency (e.g., 'usd') |
| price | FLOAT | Daily closing price |
| market_cap | FLOAT | Total market capitalization |
| volume | FLOAT | 24h trading volume |
| return | FLOAT | Daily simple return |
| log_return | FLOAT | Daily log return |
| volatility_annual_pct | FLOAT | 30-day rolling annualized volatility |
| ma_50 | FLOAT | 50-day simple moving average |
| ma_200 | FLOAT | 200-day simple moving average |
| drawdown_pct | FLOAT | Drawdown from running peak |

### crypto_snapshot
Latest single row per coin with all metrics.
Same columns as crypto_timeseries.