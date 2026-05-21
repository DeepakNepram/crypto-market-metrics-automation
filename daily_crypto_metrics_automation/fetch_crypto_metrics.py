# ── Imports ──────────────────────────────────────────────────────────────────
import os
import numpy as np
import pandas as pd
import requests
from datetime import datetime, timezone
from sqlalchemy import create_engine, types as sqltypes

# ── Config ───────────────────────────────────────────────────────────────────
COINS = [
    {"id": "bitcoin",  "symbol": "BTC"},
    {"id": "ethereum", "symbol": "ETH"},
    {"id": "solana",   "symbol": "SOL"},
]
VS_CURRENCY       = "usd"
HISTORY_DAYS      = 365
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
POSTGRES_URI      = "postgresql+psycopg2://neondb_owner:npg_yVQ1kzD0INun@ep-nameless-fog-aob2dfqo-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# ── Helper Functions ──────────────────────────────────────────────────────────
def fetch_market_chart(coin_id: str, vs_currency: str, days: int) -> dict:
    url    = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days, "interval": "daily"}
    resp   = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def market_chart_to_df(raw: dict, coin_id: str, symbol: str, vs_currency: str) -> pd.DataFrame:
    prices      = pd.DataFrame(raw["prices"],        columns=["timestamp_ms", "price"])
    market_caps = pd.DataFrame(raw["market_caps"],   columns=["timestamp_ms", "market_cap"])
    volumes     = pd.DataFrame(raw["total_volumes"], columns=["timestamp_ms", "volume"])

    df = prices.merge(market_caps, on="timestamp_ms").merge(volumes, on="timestamp_ms")
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms", utc=True)
    df = df.drop(columns=["timestamp_ms"]).set_index("timestamp").sort_index()

    df["coin_id"]      = coin_id
    df["symbol"]       = symbol
    df["vs_currency"]  = vs_currency
    return df[["coin_id", "symbol", "vs_currency", "price", "market_cap", "volume"]]


def compute_metrics(df: pd.DataFrame, window_vol: int = 30) -> pd.DataFrame:
    df = df.copy().sort_index()
    df["return"]     = df["price"].pct_change().astype(float)
    df["log_return"] = np.log(df["price"] / df["price"].shift(1))
    df["log_return"] = df["log_return"].replace([np.inf, -np.inf], np.nan).astype(float)

    df["volatility_annual_pct"] = df["return"].rolling(window_vol).std() * (365 ** 0.5) * 100
    df["ma_50"]  = df["price"].rolling(50).mean()
    df["ma_200"] = df["price"].rolling(200).mean()

    df["wealth"]       = (1 + df["return"].fillna(0)).cumprod()
    df["wealth_peak"]  = df["wealth"].expanding().max()
    df["drawdown_pct"] = (df["wealth"] / df["wealth_peak"] - 1) * 100
    return df


# ── Pipeline ──────────────────────────────────────────────────────────────────
def run_full_pipeline():
    # 1. Fetch price data
    all_dfs = []
    for c in COINS:
        print(f"Fetching {HISTORY_DAYS} days for {c['symbol']} ({c['id']})...")
        raw     = fetch_market_chart(c["id"], VS_CURRENCY, HISTORY_DAYS)
        df_coin = market_chart_to_df(raw, c["id"], c["symbol"], VS_CURRENCY)
        all_dfs.append(df_coin)

    prices_df = pd.concat(all_dfs).sort_index()

    # 2. Compute metrics
    metrics_df = (
        prices_df
        .groupby(["coin_id", "symbol", "vs_currency"], group_keys=False)
        .apply(compute_metrics)
    )

    # 3. Build snapshot
    snapshot_cols = ["coin_id", "symbol", "vs_currency", "timestamp", "price",
                     "market_cap", "volume", "return", "volatility_annual_pct",
                     "ma_50", "ma_200", "drawdown_pct"]
    latest     = metrics_df.groupby(["coin_id", "symbol", "vs_currency"]).tail(1).reset_index()
    snapshot_df = latest[["timestamp"] + [c for c in snapshot_cols if c != "timestamp"]]

    return metrics_df, snapshot_df


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    metrics_df, snapshot_df = run_full_pipeline()

    # Write summary CSV
    os.makedirs("output", exist_ok=True)
    output_path = "output/crypto_metrics_summary.csv"
    snapshot_df.to_csv(output_path, index=False)
    print(f"Written latest snapshot to {output_path}")

    # Write to Neon PostgreSQL
    engine = create_engine(POSTGRES_URI)

    metrics_out = metrics_df.sort_index().copy()
    if metrics_out.index.tz is not None:
        metrics_out.index = metrics_out.index.tz_convert(None)
    metrics_out = metrics_out.reset_index().rename(columns={"index": "timestamp"})
    metrics_out["timestamp"] = pd.to_datetime(metrics_out["timestamp"])

    snapshot_out = snapshot_df.copy()
    if snapshot_out["timestamp"].dt.tz is not None:
        snapshot_out["timestamp"] = snapshot_out["timestamp"].dt.tz_convert(None)

    dtype_map = {
        "timestamp":   sqltypes.DateTime(),
        "coin_id":     sqltypes.String(64),
        "symbol":      sqltypes.String(16),
        "vs_currency": sqltypes.String(16),
    }

    metrics_out.to_sql("crypto_timeseries", engine, if_exists="replace", index=False, dtype=dtype_map)
    snapshot_out.to_sql("crypto_snapshot",  engine, if_exists="replace", index=False, dtype=dtype_map)
    print("Data written to Neon PostgreSQL.")