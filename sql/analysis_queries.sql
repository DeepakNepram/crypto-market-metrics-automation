-- ============================================================
-- Crypto Market Metrics Automation - SQL Analysis Queries
-- Database: Neon PostgreSQL
-- Tables: crypto_timeseries, crypto_snapshot
-- Author: Deepak Nepram, IIBS Bangalore
-- Date: May 2026
-- ============================================================

--Query 1. INSPECTING LATEST SNAPSHOT OF ALL COINS
SELECT *
FROM crypto_snapshot
ORDER BY market_cap DESC

--Query 2. DAILY RETURNS FOR BITCOIN 
SELECT 
  date_trunc('day', timestamp) as day,
  symbol,
  return 
FROM crypto_timeseries
WHERE symbol = 'BTC' and return IS NOT NULL
ORDER BY day

--Query 3. AVERAGE ANNUALIZED VOLATILITY FOR EACH COIN
SELECT 
  symbol,
  avg(volatility_annual_pct) as avg_annualized_volatility
FROM crypto_timeseries
GROUP BY symbol
ORDER BY 2

--Query 4. MAXIMUM DRAWDOWN PER COIN(MORE NEGATIVE = DEEPER DRAWDOWN)
SELECT
  symbol,
  min(drawdown_pct) as max_drawdown_pct
FROM crypto_timeseries
GROUP BY symbol
ORDER BY 2 DESC

--Query 5. AVERAGE ANNUALIZED RETURN AND VOLATILITY FOR EACH COIN
WITH daily_stats as(
  SELECT
    symbol,
    AVG(return) as avg_daily_return,
    STDDEV_POP(return) as std_daily_return
  FROM crypto_timeseries
  GROUP BY symbol
)
SELECT 
  symbol,
  (avg_daily_return * 365) as approx_annual_return,
  (std_daily_return * sqrt(365)) as approx_annual_volatility
FROM daily_stats
ORDER BY 2 DESC

--Query 6. COUNTING DAYS WITH PRICES ABOVE AND BELOW MS_200
SELECT
  symbol,
  COUNT(*) FILTER(WHERE price > ma_200) AS days_above_MA_200,
  COUNT(*) FILTER(WHERE price <= ma_200) AS days_below_MA_200
FROM crypto_timeseries
GROUP BY symbol
ORDER BY 2 DESC

--Query 7. CORRELATION OF DAILY RETURNS BETWEEN TWO COINS
WITH btc as(
  SELECT 
    date_trunc('day', timestamp) as day, 
    return as btc_return
  FROM crypto_timeseries
  WHERE symbol = 'BTC'
),
eth as(
  SELECT 
    date_trunc('day', timestamp) as day,
    return as eth_return
  FROM crypto_timeseries
  WHERE symbol = 'ETH'
)
SELECT 
  corr(btc.btc_return,eth.eth_return) as corr_btc_eth
FROM btc
JOIN eth USING (day); 

--Query 8. Sharpe ratio approximation per coin(annualized)
--Assumes risk free rate (=0)
SELECT
  symbol,
  ROUND(AVG(return) :: NUMERIC, 6) as daily_avg_return,
  ROUND(STDDEV(return) :: NUMERIC, 6) as daily_volatility,
  ROUND((AVG(return) / NULLIF(STDDEV(return),0) * SQRT(365))::NUMERIC, 6) as sharpe_ratio_annualized
FROM crypto_timeseries
WHERE return IS NOT NULL
GROUP BY symbol
ORDER BY 4 DESC

--Query 9. 7 day rolling price change detection per coin(momentum signal)
WITH lagged AS(
  SELECT 
    symbol,
    timestamp,
    price,
    LAG(price,7) OVER (PARTITION BY symbol ORDER BY timestamp) as price_7d_ago
  FROM crypto_timeseries
)
SELECT 
  symbol,
  timestamp,
  ROUND(price::NUMERIC, 2) as current_price,
  ROUND(price_7d_ago::NUMERIC, 2) as price_7d_agp,
  ROUND(((price - price_7d_ago) / NULLIF(price_7d_ago, 0) * 100)::NUMERIC, 2) AS price_change_7d_pct,
  CASE 
  WHEN (price - price_7d_ago) / NULLIF(price_7d_ago, 0) > 0.5 THEN 'Strong Uptrend'
  WHEN (price - price_7d_ago) / NULLIF(price_7d_ago, 0) > 0 THEN 'Mild Uptrend'
  WHEN (price - price_7d_ago) / NULLIF(price_7d_ago, 0) < -0.5 THEN 'Strong Downtrend'
  ELSE 'Mild Downtrend'
  END as momentum_signal
FROM lagged
WHERE price_7d_ago IS NOT NULL
ORDER BY symbol, timestamp DESC

--Query 10. longest consequetive neagtive return streak per --coin(Drawdown Depth Analysis)
WITH return_flags as(
  SELECT 
    symbol,
    timestamp,
    return,
    CASE WHEN return > 0 THEN 1 ELSE 0 END as is_loss_day
  FROM crypto_timeseries
  WHERE return IS NOT NULL
),
grouped as(
  SELECT 
    symbol,
    timestamp,
    return,
    is_loss_day,
    SUM(CASE WHEN is_loss_day = 0 THEN 1 ELSE 0 END) OVER (PARTITION BY symbol ORDER BY timestamp) as streak_group
  FROM return_flags
),
streaks as(
  SELECT
    symbol,
    streak_group,
    COUNT(*) as consequetive_loss_days,
    MIN(timestamp) as streak_start,
    MAX(timestamp) as streak_end,
    ROUND(SUM(return)::NUMERIC, 8) as total_return_during_streak
  FROM grouped
  WHERE is_loss_day = 1
  GROUP BY symbol, streak_group
)
SELECT 
  symbol,
  MAX(consequetive_loss_days) as longest_loss_streak_days,
  MIN(total_return_during_streak) as worst_streak_cumulative_return
FROM streaks
GROUP BY symbol
ORDER BY 2 DESC



  

