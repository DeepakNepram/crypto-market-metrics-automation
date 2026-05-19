# 📊 Crypto Market Metrics Automation

> An end-to-end automated analytics pipeline that fetches real-time crypto data,
> computes risk/return metrics, stores them in a cloud PostgreSQL database,
> and visualizes them in an Apache Superset dashboard.

![Dashboard Screenshot](dashboard/dashboard_screenshot.png)

---

## 🚀 Project Overview

This project automates the full lifecycle of crypto market analytics:

- **Fetches** daily OHLCV data for BTC, ETH, and SOL from the CoinGecko API
- **Computes** 9 financial metrics including returns, volatility, drawdown, Sharpe Ratio, and 7-day momentum
- **Stores** results in a cloud-hosted Neon PostgreSQL database
- **Visualizes** everything in a multi-chart Apache Superset dashboard
- **Analyzes** with 10 reusable SQL queries in the Neon SQL Editor

---

## 🏗️ Architecture
CoinGecko API
↓
Google Colab (Python + pandas)
↓
Neon PostgreSQL (cloud database)
↓
Apache Superset (Docker) → Hero Dashboard


---

## 📁 Project Structure
crypto-market-metrics-automation/
├── notebooks/ → Google Colab pipeline notebook
├── sql/ → 10 analysis queries + schema notes
├── dashboard/ → Superset export ZIP + screenshot
├── presentation/ → Key findings slide deck (PDF)
├── assets/ → Architecture diagram
├── .gitignore
├── LICENSE → MIT
├── requirements.txt
└── README.md


---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Data Source | CoinGecko Free API |
| Compute | Python 3, pandas, NumPy |
| Environment | Google Colab |
| Database | Neon PostgreSQL (serverless) |
| DB Connector | SQLAlchemy + psycopg2 |
| BI Dashboard | Apache Superset (Docker) |
| Version Control | GitHub |

---

## 📊 Metrics Computed

| Metric | Description |
|--------|-------------|
| Daily Return | Simple percentage return |
| Log Return | Natural log return |
| Annualized Volatility | 30-day rolling std × √365 |
| 50-day MA | Short-term trend line |
| 200-day MA | Long-term trend line |
| Drawdown % | % decline from running peak |
| Sharpe Ratio | Risk-adjusted return (annualized) |
| 7-Day Momentum Signal | Strong/Mild Up/Downtrend label |
| Consecutive Loss Streak | Longest run of negative return days |

---

## ⚙️ Setup Instructions

### 1. Run the data pipeline

Open `notebooks/crypto_metrics_pipeline.ipynb` in Google Colab.

Update `POSTGRES_URI` in Cell 2 with your own Neon connection string:
```python
POSTGRES_URI = "postgresql+psycopg2://user:pass@host/db?sslmode=require"
```

Run all cells sequentially.

### 2. Set up Apache Superset locally

```bash
git clone https://github.com/apache/superset.git
cd superset
git checkout tags/6.0.0
docker compose -f docker-compose-non-dev.yml up
```

Open http://localhost:8088 (admin / admin)

### 3. Import the dashboard

1. In Superset, go to **Dashboards → Import Dashboard**
2. Upload `dashboard/dashboard_export.zip`
3. Connect your own Neon database under **Settings → Database Connections**
4. Refresh all datasets

See `dashboard/dashboard_notes.md` for full details.

---

## 🔍 Key Findings

- **BTC** showed the lowest annualized volatility (~42%) among the three assets
- **SOL** had the highest Sharpe Ratio, indicating superior risk-adjusted return
- All three assets experienced max drawdowns exceeding 30% during the observation period
- BTC-ETH daily return correlation was ~0.85, confirming high co-movement

See `presentation/crypto_metrics_key_findings.pdf` for the full analysis.

---

## 📋 SQL Queries

10 reusable queries are available in `sql/analysis_queries.sql`, covering:

1. Latest snapshot per coin
2. Daily return time series
3. Average volatility by coin
4. Max drawdown per coin
5. Risk-return profile (annualized)
6. Trend regime count (above/below 200MA)
7. BTC-ETH return correlation
8. Sharpe Ratio approximation
9. 7-day momentum signal
10. Consecutive loss streak analysis

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Deepak Nepram**
PGDM – Business Analytics & Data Science
IIBS Bangalore | May 2026

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/your-profile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/your-username)