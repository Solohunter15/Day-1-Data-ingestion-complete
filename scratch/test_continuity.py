import sqlite3
import pandas as pd
import numpy as np

# Connect to database
db_path = 'data/db/bluestock_mf.db'
conn = sqlite3.connect(db_path)

# Load transactions
df_tx = pd.read_sql_query("SELECT investor_id, transaction_date, transaction_type FROM fact_transactions WHERE transaction_type = 'SIP'", conn)
df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])

# Count SIPs per investor
sip_counts = df_tx['investor_id'].value_counts()
eligible_investors = sip_counts[sip_counts >= 6].index

print(f"Total investors with SIPs: {df_tx['investor_id'].nunique()}")
print(f"Investors with 6+ SIPs: {len(eligible_investors)}")

# Filter transactions for eligible investors
df_eligible = df_tx[df_tx['investor_id'].isin(eligible_investors)].copy()
df_eligible.sort_values(by=['investor_id', 'transaction_date'], inplace=True)

# Calculate gaps
df_eligible['prev_date'] = df_eligible.groupby('investor_id')['transaction_date'].shift(1)
df_eligible['gap_days'] = (df_eligible['transaction_date'] - df_eligible['prev_date']).dt.days

# Calculate average and max gaps per investor
investor_gaps = df_eligible.groupby('investor_id').agg(
    avg_gap=('gap_days', 'mean'),
    max_gap=('gap_days', 'max'),
    sip_count=('transaction_type', 'count')
).reset_index()

# Flag at-risk
investor_gaps['at_risk_by_avg'] = investor_gaps['avg_gap'] > 35
investor_gaps['at_risk_by_max'] = investor_gaps['max_gap'] > 35

print("\nSummary of Gaps:")
print(investor_gaps.describe())

print("\nFlagged 'at-risk' by average gap > 35 days:")
print(investor_gaps['at_risk_by_avg'].value_counts())

print("\nFlagged 'at-risk' by maximum gap > 35 days:")
print(investor_gaps['at_risk_by_max'].value_counts())

conn.close()
