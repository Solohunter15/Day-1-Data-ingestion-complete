import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_all_analysis():
    # 1. Setup paths
    db_path = 'data/db/bluestock_mf.db'
    bench_csv = 'data/raw/10_benchmark_indices.csv'
    report_csv = 'var_cvar_report.csv'
    chart_png = 'rolling_sharpe_chart.png'

    print("--- Connecting to Database ---")
    conn = sqlite3.connect(db_path)

    # Load fund master metadata and daily NAV history
    df_funds = pd.read_sql_query("SELECT amfi_code, scheme_name, fund_house, category, sub_category, plan, risk_category FROM dim_fund", conn)
    df_nav = pd.read_sql_query("SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date", conn)
    df_nav['date'] = pd.to_datetime(df_nav['date'])

    # Load benchmark data for date alignment
    df_bench = pd.read_csv(bench_csv)
    df_bench['date'] = pd.to_datetime(df_bench['date'])

    # Align dates with Nifty 100 trading days
    df_n100 = df_bench[df_bench["index_name"] == "NIFTY100"].rename(columns={"close_value": "nifty100_close"})
    df_aligned = pd.merge(df_nav, df_n100[["date", "nifty100_close"]], on="date", how="inner")
    df_aligned = pd.merge(df_aligned, df_funds, on="amfi_code", how="inner")
    df_aligned.sort_values(["amfi_code", "date"], inplace=True)

    print(f"Total aligned NAV rows: {len(df_aligned)} ({len(df_aligned)/len(df_funds):.1f} days per scheme)")

    # Compute daily returns
    df_aligned["daily_return"] = df_aligned.groupby("amfi_code")["nav"].pct_change()

    # ==========================================
    # Task 1: Historical VaR (95%) and CVaR
    # ==========================================
    print("\n--- Task 1: Historical VaR (95%) & CVaR ---")
    var_results = []
    for amfi_code, group in df_aligned.groupby("amfi_code"):
        returns = group["daily_return"].dropna()
        if len(returns) == 0:
            continue
        scheme_name = group["scheme_name"].iloc[0]
        risk_category = group["risk_category"].iloc[0]
        
        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean()
        
        var_results.append({
            "amfi_code": amfi_code,
            "scheme_name": scheme_name,
            "risk_grade": risk_category,
            "historical_var_95": var_95,
            "cvar_95": cvar_95,
            "historical_var_95_pct": var_95 * 100,
            "cvar_95_pct": cvar_95 * 100
        })
        
    df_var = pd.DataFrame(var_results)
    df_var.to_csv(report_csv, index=False)
    print(f"Saved VaR/CVaR report for {len(df_var)} funds to {report_csv}")
    print(df_var.sort_values(by="historical_var_95").head(5))

    # ==========================================
    # Task 2: Rolling 90-day Sharpe Ratio
    # ==========================================
    print("\n--- Task 2: Rolling 90-day Sharpe Ratio ---")
    key_funds = [119551, 100016, 120503, 118632, 120841]
    df_key = df_aligned[df_aligned['amfi_code'].isin(key_funds)].copy()
    
    df_key['rolling_mean'] = df_key.groupby('amfi_code')['daily_return'].transform(lambda x: x.rolling(90).mean())
    df_key['rolling_std'] = df_key.groupby('amfi_code')['daily_return'].transform(lambda x: x.rolling(90).std())
    df_key['rolling_sharpe'] = (df_key['rolling_mean'] / df_key['rolling_std']) * np.sqrt(252)

    # Plot rolling Sharpe over time
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 6.5), dpi=150)
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for idx, code in enumerate(key_funds):
        fund_data = df_key[df_key['amfi_code'] == code].sort_values('date')
        name = fund_data['scheme_name'].iloc[0].split(" - ")[0] # Clean up name
        plt.plot(fund_data['date'], fund_data['rolling_sharpe'], label=name, color=colors[idx], linewidth=1.5)
        
    plt.title("Rolling 90-Day Sharpe Ratio Over Time (2022–2026)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Date", fontsize=11, labelpad=10)
    plt.ylabel("Rolling Sharpe Ratio (Annualized)", fontsize=11, labelpad=10)
    plt.legend(title="Key Mutual Funds", title_fontsize='11', loc='upper left', frameon=True, shadow=True)
    plt.tight_layout()
    plt.savefig(chart_png)
    plt.close()
    print(f"Saved rolling Sharpe chart to {chart_png}")

    # ==========================================
    # Task 3: Investor Cohort Analysis
    # ==========================================
    print("\n--- Task 3: Investor Cohort Analysis ---")
    df_tx = pd.read_sql_query("SELECT investor_id, transaction_date, amfi_code, transaction_type, amount_inr FROM fact_transactions", conn)
    df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
    
    # Cohort assignment
    df_first_tx = df_tx.groupby('investor_id')['transaction_date'].min().reset_index()
    df_first_tx.rename(columns={'transaction_date': 'first_tx_date'}, inplace=True)
    df_first_tx['cohort_year'] = df_first_tx['first_tx_date'].dt.year
    df_tx = pd.merge(df_tx, df_first_tx[['investor_id', 'cohort_year']], on='investor_id', how='inner')
    
    cohort_results = []
    for cohort_year, group in df_tx.groupby('cohort_year'):
        sip_group = group[group['transaction_type'] == 'SIP']
        avg_sip = sip_group['amount_inr'].mean() if len(sip_group) > 0 else 0
        
        gross_invested = group[group['transaction_type'].isin(['SIP', 'Lumpsum'])]['amount_inr'].sum()
        net_invested = gross_invested - group[group['transaction_type'] == 'Redemption']['amount_inr'].sum()
        
        # Top fund by amount invested
        buy_group = group[group['transaction_type'].isin(['SIP', 'Lumpsum'])]
        fund_amounts = buy_group.groupby('amfi_code')['amount_inr'].sum().reset_index()
        if len(fund_amounts) > 0:
            top_fund_code = fund_amounts.sort_values(by='amount_inr', ascending=False).iloc[0]['amfi_code']
            top_fund_name = df_funds[df_funds['amfi_code'] == top_fund_code]['scheme_name'].iloc[0]
            top_fund_amt = fund_amounts.sort_values(by='amount_inr', ascending=False).iloc[0]['amount_inr']
        else:
            top_fund_name, top_fund_amt = "N/A", 0
            
        # Top fund by transaction count
        fund_counts = buy_group.groupby('amfi_code').size().reset_index(name='count')
        if len(fund_counts) > 0:
            top_count_code = fund_counts.sort_values(by='count', ascending=False).iloc[0]['amfi_code']
            top_count_name = df_funds[df_funds['amfi_code'] == top_count_code]['scheme_name'].iloc[0]
            top_count_val = fund_counts.sort_values(by='count', ascending=False).iloc[0]['count']
        else:
            top_count_name, top_count_val = "N/A", 0

        cohort_results.append({
            "cohort_year": cohort_year,
            "investor_count": group['investor_id'].nunique(),
            "avg_sip_amount": avg_sip,
            "gross_invested": gross_invested,
            "net_invested": net_invested,
            "top_fund_by_amount": top_fund_name,
            "top_fund_amount": top_fund_amt,
            "top_fund_by_count": top_count_name,
            "top_fund_count": top_count_val
        })
        
    df_cohort = pd.DataFrame(cohort_results)
    print(df_cohort)

    # ==========================================
    # Task 4: SIP Continuity Analysis
    # ==========================================
    print("\n--- Task 4: SIP Continuity Analysis ---")
    df_sip = df_tx[df_tx['transaction_type'] == 'SIP'].copy()
    sip_counts = df_sip['investor_id'].value_counts()
    eligible_investors = sip_counts[sip_counts >= 6].index
    
    df_eligible = df_sip[df_sip['investor_id'].isin(eligible_investors)].copy()
    df_eligible.sort_values(by=['investor_id', 'transaction_date'], inplace=True)
    df_eligible['prev_date'] = df_eligible.groupby('investor_id')['transaction_date'].shift(1)
    df_eligible['gap_days'] = (df_eligible['transaction_date'] - df_eligible['prev_date']).dt.days
    
    investor_gaps = df_eligible.groupby('investor_id').agg(
        avg_gap=('gap_days', 'mean'),
        max_gap=('gap_days', 'max'),
        sip_count=('transaction_type', 'count')
    ).reset_index()
    
    investor_gaps['at_risk'] = investor_gaps['avg_gap'] > 35
    at_risk_count = investor_gaps['at_risk'].sum()
    total_eligible = len(investor_gaps)
    continuity_rate = (total_eligible - at_risk_count) / total_eligible * 100
    
    print(f"Total eligible investors (6+ SIP transactions): {total_eligible}")
    print(f"At-risk investors (avg gap > 35 days): {at_risk_count} ({at_risk_count/total_eligible*100:.2f}%)")
    print(f"Continuous (healthy) investors: {total_eligible - at_risk_count} ({continuity_rate:.2f}%)")
    print(f"Global average gap: {investor_gaps['avg_gap'].mean():.2f} days")
    print(f"Global max gap observed: {investor_gaps['max_gap'].max():.2f} days")

    # ==========================================
    # Task 6: Sector HHI Concentration
    # ==========================================
    print("\n--- Task 6: Sector HHI Concentration ---")
    df_portfolio = pd.read_sql_query("SELECT amfi_code, stock_symbol, stock_name, sector, weight_pct FROM fact_portfolio", conn)
    
    # Filter for equity funds
    df_equity_funds = df_funds[df_funds['category'] == 'Equity']
    df_portfolio = df_portfolio[df_portfolio['amfi_code'].isin(df_equity_funds['amfi_code'])].copy()
    
    df_sec_weight = df_portfolio.groupby(['amfi_code', 'sector'])['weight_pct'].sum().reset_index()
    
    df_hhi = df_sec_weight.groupby('amfi_code').apply(
        lambda g: pd.Series({
            'hhi_percentage': np.sum(g['weight_pct'] ** 2),
            'hhi_decimal': np.sum((g['weight_pct'] / 100) ** 2),
            'sector_count': g['sector'].nunique()
        }), include_groups=False
    ).reset_index()
    
    df_hhi = pd.merge(df_hhi, df_funds[['amfi_code', 'scheme_name']], on='amfi_code')
    df_hhi.sort_values(by='hhi_percentage', ascending=False, inplace=True)
    
    print("\nTop 5 Concentrated Funds (Highest Sector HHI):")
    print(df_hhi.head(5)[['scheme_name', 'hhi_percentage', 'sector_count']])
    
    print("\nTop 5 Diversified Funds (Lowest Sector HHI):")
    print(df_hhi.tail(5)[['scheme_name', 'hhi_percentage', 'sector_count']])

    conn.close()

if __name__ == '__main__':
    run_all_analysis()
