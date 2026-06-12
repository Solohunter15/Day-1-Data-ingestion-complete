import sqlite3
import pandas as pd
import numpy as np

# Connect to database
db_path = 'data/db/bluestock_mf.db'
conn = sqlite3.connect(db_path)

# Load holdings and funds
df_portfolio = pd.read_sql_query("SELECT amfi_code, stock_symbol, stock_name, sector, weight_pct FROM fact_portfolio", conn)
df_funds = pd.read_sql_query("SELECT amfi_code, scheme_name, category FROM dim_fund", conn)

# Filter for equity funds
df_equity_funds = df_funds[df_funds['category'] == 'Equity']
df_portfolio = df_portfolio[df_portfolio['amfi_code'].isin(df_equity_funds['amfi_code'])].copy()

# Group holdings by fund and sector to find sector weights
df_sector_weight = df_portfolio.groupby(['amfi_code', 'sector'])['weight_pct'].sum().reset_index()

# Compute HHI = sum(weight_pct^2) for each fund
df_hhi = df_sector_weight.groupby('amfi_code').apply(
    lambda g: pd.Series({
        'hhi_percentage': np.sum(g['weight_pct'] ** 2),
        'hhi_decimal': np.sum((g['weight_pct'] / 100) ** 2),
        'sector_count': g['sector'].nunique()
    }), include_groups=False
).reset_index()

# Merge with fund master to get scheme names
df_hhi = pd.merge(df_hhi, df_funds[['amfi_code', 'scheme_name']], on='amfi_code')
df_hhi.sort_values(by='hhi_percentage', ascending=False, inplace=True)

print("Sector HHI Concentration ranking (Top 10 concentrated funds):")
print(df_hhi.head(10))

print("\nTop 5 most diversified funds (lowest HHI):")
print(df_hhi.tail(5))

conn.close()
