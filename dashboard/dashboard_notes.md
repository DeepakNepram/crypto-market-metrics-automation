## Dashboard Import Instructions

1. Run Apache Superset locally with Docker:
docker compose -f docker-compose-non-dev.yml up

2. Open http://localhost:8088 and log in (admin/admin).
3. Go to Dashboards → Import Dashboard.
4. Upload `dashboard_export.zip` from this folder.
5. Connect the database to your own PostgreSQL/Neon instance.
6. Refresh all datasets.

## Dashboard Contents
- Row 1: Big Number KPIs (Price, Volatility, Drawdown)
- Row 2: Price + 50MA + 200MA Line Chart
- Row 3: Volatility Bar Chart + Drawdown Area Chart
- Row 4: Risk-Return Scatter + 7-Day Momentum Table + Volume Chart