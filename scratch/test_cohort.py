import sqlite3
import pandas as pd
import numpy as np

# Connect to database
db_path = 'data/db/bluestock_mf.db'
conn = sqlite3.connect(db_path)

# Load transactions and funds
df_tx = pd.read_sql_query("SELECT investor_id, transaction_date, amfi_code, transaction_type, amount_inr FROM fact_transactions", conn)
df_funds = pd.read_sql_query("SELECT amfi_code, scheme_name FROM dim_fund", conn)

df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
df_tx['year'] = df_tx['transaction_date'].dt.year

print("Transaction count:", len(df_tx))
print("Unique transaction types:", df_tx['transaction_type'].unique())
print("Unique years in transaction dates:", df_tx['year'].unique())

# Find first transaction date per investor
df_first_tx = df_tx.groupby('investor_id')['transaction_date'].min().reset_index()
df_first_tx.rename(columns={'transaction_date': 'first_tx_date'}, inplace=True)
df_first_tx['cohort_year'] = df_first_tx['first_tx_date'].dt.year

# Merge back to transaction data
df_tx = pd.merge(df_tx, df_first_tx, on='investor_id', how='inner')

print("\nInvestor counts by cohort:")
print(df_first_tx['cohort_year'].value_counts())

# Cohort Analysis
cohort_groups = df_tx.groupby('cohort_year')

cohort_results = []
for name, group in cohort_groups:
    # Average SIP amount
    sip_group = group[group['transaction_type'] == 'SIP']
    avg_sip = sip_group['amount_inr'].mean() if len(sip_group) > 0 else 0
    
    # Total Invested (gross: SIP + Lumpsum)
    gross_invested = group[group['transaction_type'].isin(['SIP', 'Lumpsum'])]['amount_inr'].sum()
    
    # Total Invested (net: SIP + Lumpsum - Redemption)
    net_invested = gross_invested - group[group['transaction_type'] == 'Redemption']['amount_inr'].sum()
    
    # Top fund preference (by total amount invested in SIP/Lumpsum)
    buy_group = group[group['transaction_type'].isin(['SIP', 'Lumpsum'])]
    fund_amounts = buy_group.groupby('amfi_code')['amount_inr'].sum().reset_index()
    if len(fund_amounts) > 0:
        top_fund_code = fund_amounts.sort_values(by='amount_inr', ascending=False).iloc[0]['amfi_code']
        top_fund_name = df_funds[df_funds['amfi_code'] == top_fund_code]['scheme_name'].iloc[0]
        top_fund_amt = fund_amounts.sort_values(by='amount_inr', ascending=False).iloc[0]['amount_inr']
    else:
        top_fund_name = "N/A"
        top_fund_amt = 0
        
    cohort_results.append({
        "cohort_year": name,
        "investor_count": group['investor_id'].nunique(),
        "avg_sip_amount": avg_sip,
        "gross_invested": gross_invested,
        "net_invested": net_invested,
        "top_fund_preference": top_fund_name,
        "top_fund_total_amount": top_fund_amt
    })

df_cohort = pd.DataFrame(cohort_results)
print("\nCohort Analysis Results:")
print(df_cohort)

conn.close()
