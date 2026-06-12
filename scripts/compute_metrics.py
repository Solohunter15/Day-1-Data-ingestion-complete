"""
Bluestock Mutual Fund Analytics Platform - Performance & Advanced Risk Metrics
Computes CAGR, Sharpe/Sortino ratios, Alpha/Beta vs Nifty 100, Max Drawdown,
Value at Risk (95% VaR / CVaR), Sector HHI, and the composite scorecard.
Updates fact_performance in SQLite and saves analytics CSVs and PNG charts.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
import seaborn as sns

# Set up paths relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "db", "bluestock_mf.db")
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
CHARTS_DIR = os.path.join(REPORTS_DIR, "charts")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# Plotting style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["figure.dpi"] = 150

def run_performance_calculations():
    print("=" * 60)
    print("STARTING PERFORMANCE & RISK CALCULATIONS")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Load metadata
    df_funds = pd.read_sql_query("""
        SELECT amfi_code, scheme_name, fund_house, category, sub_category, plan, expense_ratio_pct, risk_category 
        FROM dim_fund
    """, conn)
    
    # Load daily NAV history
    df_nav = pd.read_sql_query("""
        SELECT amfi_code, date, nav 
        FROM fact_nav 
        ORDER BY amfi_code, date
    """, conn)
    df_nav["date"] = pd.to_datetime(df_nav["date"])
    
    # Load benchmark closing prices for calendar alignment
    bench_csv = os.path.join(RAW_DIR, "10_benchmark_indices.csv")
    df_bench = pd.read_csv(bench_csv)
    df_bench["date"] = pd.to_datetime(df_bench["date"])
    
    df_n50 = df_bench[df_bench["index_name"] == "NIFTY50"].rename(columns={"close_value": "nifty50_close"})
    df_n100 = df_bench[df_bench["index_name"] == "NIFTY100"].rename(columns={"close_value": "nifty100_close"})
    df_benchmarks = pd.merge(df_n50[["date", "nifty50_close"]], df_n100[["date", "nifty100_close"]], on="date", how="inner")
    
    # Align NAV history with benchmark trading calendar
    df_aligned = pd.merge(df_nav, df_benchmarks, on="date", how="inner")
    df_aligned = pd.merge(df_aligned, df_funds, on="amfi_code", how="inner")
    df_aligned.sort_values(["amfi_code", "date"], inplace=True)
    
    # Daily returns
    df_aligned["fund_return"] = df_aligned.groupby("amfi_code")["nav"].pct_change()
    df_aligned["nifty50_return"] = df_aligned.groupby("amfi_code")["nifty50_close"].pct_change()
    df_aligned["nifty100_return"] = df_aligned.groupby("amfi_code")["nifty100_close"].pct_change()
    
    df_ret_clean = df_aligned.dropna(subset=["fund_return"]).copy()
    
    # Load static info from original schema performance file
    perf_orig_path = os.path.join(RAW_DIR, "07_scheme_performance.csv")
    df_perf_orig = pd.read_csv(perf_orig_path)
    static_info = df_perf_orig[["amfi_code", "aum_crore", "morningstar_rating", "risk_grade"]].set_index("amfi_code").to_dict("index")
    
    # Calculate performance metrics
    results = []
    Rf = 0.065
    Rf_daily = Rf / 252
    
    for amfi in df_funds["amfi_code"]:
        df_f = df_ret_clean[df_ret_clean["amfi_code"] == amfi].copy()
        if len(df_f) == 0:
            continue
            
        fund_info = df_funds[df_funds["amfi_code"] == amfi].iloc[0]
        
        fund_ret_series = df_f["fund_return"]
        mean_daily = fund_ret_series.mean()
        std_daily = fund_ret_series.std()
        
        # NAV values
        nav_end = df_f["nav"].iloc[-1]
        
        # 1yr start: closest to 2025-05-29
        idx_1yr = (df_f["date"] - pd.Timestamp("2025-05-29")).abs().idxmin()
        nav_1yr = df_f.loc[idx_1yr, "nav"]
        cagr_1yr = (nav_end / nav_1yr) - 1
        
        # 3yr start: closest to 2023-05-29
        idx_3yr = (df_f["date"] - pd.Timestamp("2023-05-29")).abs().idxmin()
        nav_3yr = df_f.loc[idx_3yr, "nav"]
        cagr_3yr = (nav_end / nav_3yr) ** (1/3.0) - 1
        
        # 5yr (full period 4.4 years) start: first date (2022-01-03)
        nav_start = df_f["nav"].iloc[0]
        n_years = (df_f["date"].iloc[-1] - df_f["date"].iloc[0]).days / 365.25
        cagr_5yr = (nav_end / nav_start) ** (1/n_years) - 1
        
        # Benchmarks comparison: 3yr CAGR for Nifty 100
        n100_start_val = df_f["nifty100_close"].loc[idx_3yr]
        n100_end_val = df_f["nifty100_close"].iloc[-1]
        bench_3yr = (n100_end_val / n100_start_val) ** (1/3.0) - 1
        
        # Sharpe
        sharpe = (mean_daily - Rf_daily) / std_daily * np.sqrt(252) if std_daily > 0 else 0
        
        # Sortino
        neg_returns = fund_ret_series[fund_ret_series < 0]
        downside_std_daily = neg_returns.std()
        sortino = (mean_daily - Rf_daily) / downside_std_daily * np.sqrt(252) if downside_std_daily > 0 else 0
        
        # Alpha & Beta vs Nifty 100
        slope, intercept, r_val, p_val, std_err = scipy.stats.linregress(df_f["nifty100_return"], fund_ret_series)
        beta = slope
        alpha = intercept * 252
        
        # Max Drawdown
        nav_series = df_f["nav"].values
        running_max = np.maximum.accumulate(nav_series)
        drawdowns = nav_series / running_max - 1
        max_dd = drawdowns.min()
        
        # Static metadata from original CSV
        static = static_info.get(amfi, {"aum_crore": 1000, "morningstar_rating": 3, "risk_grade": fund_info["risk_category"]})
        
        results.append({
            "amfi_code": amfi,
            "scheme_name": fund_info["scheme_name"],
            "fund_house": fund_info["fund_house"],
            "category": fund_info["category"],
            "plan": fund_info["plan"],
            "return_1yr_pct": cagr_1yr * 100,
            "return_3yr_pct": cagr_3yr * 100,
            "return_5yr_pct": cagr_5yr * 100,
            "benchmark_3yr_pct": bench_3yr * 100,
            "alpha": alpha * 100,
            "beta": beta,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "std_dev_ann_pct": std_daily * np.sqrt(252) * 100,
            "max_drawdown_pct": max_dd * 100,
            "aum_crore": static["aum_crore"],
            "expense_ratio_pct": fund_info["expense_ratio_pct"],
            "morningstar_rating": static["morningstar_rating"],
            "risk_grade": static["risk_grade"]
        })
        
    df_metrics = pd.DataFrame(results)
    
    # Save computed metrics back into database table fact_performance
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fact_performance")
    
    for _, row in df_metrics.iterrows():
        cursor.execute("""
            INSERT INTO fact_performance (
                amfi_code, scheme_name, fund_house, category, plan, 
                return_1yr_pct, return_3yr_pct, return_5yr_pct, benchmark_3yr_pct, 
                alpha, beta, sharpe_ratio, sortino_ratio, std_dev_ann_pct, 
                max_drawdown_pct, aum_crore, expense_ratio_pct, morningstar_rating, risk_grade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(row["amfi_code"]), row["scheme_name"], row["fund_house"], row["category"], row["plan"],
            float(row["return_1yr_pct"]), float(row["return_3yr_pct"]), float(row["return_5yr_pct"]), float(row["benchmark_3yr_pct"]),
            float(row["alpha"]), float(row["beta"]), float(row["sharpe_ratio"]), float(row["sortino_ratio"]),
            float(row["std_dev_ann_pct"]), float(row["max_drawdown_pct"]), int(row["aum_crore"]),
            float(row["expense_ratio_pct"]), int(row["morningstar_rating"]), row["risk_grade"]
        ))
        
    conn.commit()
    print("Updated database table 'fact_performance' with computed metrics.")
    
    # ----------------------------------------------------
    # Scorecard Calculation
    # ----------------------------------------------------
    N = len(df_metrics)
    df_metrics["rank_3yr"] = df_metrics["return_3yr_pct"].rank(ascending=True)
    df_metrics["rank_sharpe"] = df_metrics["sharpe_ratio"].rank(ascending=True)
    df_metrics["rank_alpha"] = df_metrics["alpha"].rank(ascending=True)
    df_metrics["rank_expense"] = df_metrics["expense_ratio_pct"].rank(ascending=False)
    df_metrics["rank_max_dd"] = df_metrics["max_drawdown_pct"].rank(ascending=True) # smaller magnitude (less negative) is better, but rank ascending puts worst (most negative) at 1. Wait, let's check: rank ascending means most negative (worst drawdown) gets 1, and least negative (best drawdown) gets 40. Yes, so rank ascending makes least negative (best) get 40, which is correct!
    
    df_metrics["score_3yr"] = (df_metrics["rank_3yr"] - 1) / (N - 1) * 100
    df_metrics["score_sharpe"] = (df_metrics["rank_sharpe"] - 1) / (N - 1) * 100
    df_metrics["score_alpha"] = (df_metrics["rank_alpha"] - 1) / (N - 1) * 100
    df_metrics["score_expense"] = (df_metrics["rank_expense"] - 1) / (N - 1) * 100
    df_metrics["score_max_dd"] = (df_metrics["rank_max_dd"] - 1) / (N - 1) * 100
    
    df_metrics["fund_score"] = (
        0.30 * df_metrics["score_3yr"] +
        0.25 * df_metrics["score_sharpe"] +
        0.20 * df_metrics["score_alpha"] +
        0.15 * df_metrics["score_expense"] +
        0.10 * df_metrics["score_max_dd"]
    )
    
    scorecard = df_metrics.sort_values("fund_score", ascending=False).reset_index(drop=True)
    scorecard_path = os.path.join(PROCESSED_DIR, "fund_scorecard.csv")
    scorecard.to_csv(scorecard_path, index=False)
    print(f"Saved Fund Scorecard (0-100) to {scorecard_path}")
    
    # ----------------------------------------------------
    # Benchmark Comparison Chart
    # ----------------------------------------------------
    top_5_amfi = scorecard["amfi_code"].head(5).tolist()
    available_dates = df_aligned["date"].unique()
    start_date = available_dates[np.abs(available_dates - np.datetime64("2023-05-29")).argmin()]
    end_date = df_aligned["date"].max()
    
    df_3yr_analysis = df_aligned[(df_aligned["date"] >= start_date) & (df_aligned["date"] <= end_date)].copy()
    
    plt.figure(figsize=(12, 7))
    df_bench_3yr = df_benchmarks[(df_benchmarks["date"] >= start_date) & (df_benchmarks["date"] <= end_date)].sort_values("date").copy()
    n50_start = df_bench_3yr["nifty50_close"].iloc[0]
    n100_start = df_bench_3yr["nifty100_close"].iloc[0]
    
    plt.plot(df_bench_3yr["date"], 100.0 * df_bench_3yr["nifty100_close"] / n100_start, label="Nifty 100 (Benchmark)", color="#333333", linewidth=2.5, linestyle="--")
    plt.plot(df_bench_3yr["date"], 100.0 * df_bench_3yr["nifty50_close"] / n50_start, label="Nifty 50", color="#888888", linewidth=1.8, linestyle=":")
    
    colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd", "#e377c2"]
    for i, amfi in enumerate(top_5_amfi):
        df_f = df_3yr_analysis[df_3yr_analysis["amfi_code"] == amfi].sort_values("date").copy()
        nav_start_val = df_f["nav"].iloc[0]
        plt.plot(df_f["date"], 100.0 * df_f["nav"] / nav_start_val, label=df_f["scheme_name"].iloc[0][:35], color=colors[i], linewidth=2.0)
        
    plt.title("3-Year Cumulative Growth: Top 5 Scorecard Funds vs Benchmarks (Base 100)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Date", fontsize=12, labelpad=10)
    plt.ylabel("Normalized Value (Growth of Rs. 100)", fontsize=12, labelpad=10)
    plt.legend(loc="upper left", fontsize=10)
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %Y"))
    plt.tight_layout()
    
    chart_path = os.path.join(CHARTS_DIR, "benchmark_comparison.png")
    plt.savefig(chart_path, dpi=150)
    plt.close()
    print(f"Saved Benchmark Comparison Chart to {chart_path}")
    
    # ----------------------------------------------------
    # VaR and CVaR Calculation
    # ----------------------------------------------------
    var_results = []
    for amfi_code, group in df_ret_clean.groupby("amfi_code"):
        returns = group["fund_return"].dropna()
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
    var_path = os.path.join(PROCESSED_DIR, "var_cvar_report.csv")
    df_var.to_csv(var_path, index=False)
    print(f"Saved VaR/CVaR Report to {var_path}")
    
    # ----------------------------------------------------
    # Rolling Sharpe Chart (90-Day) for Key Funds
    # ----------------------------------------------------
    key_funds = [119551, 100016, 120503, 118632, 120841]
    df_key = df_ret_clean[df_ret_clean['amfi_code'].isin(key_funds)].copy()
    
    df_key['rolling_mean'] = df_key.groupby('amfi_code')['fund_return'].transform(lambda x: x.rolling(90).mean())
    df_key['rolling_std'] = df_key.groupby('amfi_code')['fund_return'].transform(lambda x: x.rolling(90).std())
    df_key['rolling_sharpe'] = (df_key['rolling_mean'] / df_key['rolling_std']) * np.sqrt(252)
    
    plt.figure(figsize=(12, 6.5), dpi=150)
    colors_key = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for idx, code in enumerate(key_funds):
        fund_data = df_key[df_key['amfi_code'] == code].sort_values('date')
        if len(fund_data) == 0:
            continue
        name = fund_data['scheme_name'].iloc[0].split(" - ")[0]
        plt.plot(fund_data['date'], fund_data['rolling_sharpe'], label=name, color=colors_key[idx], linewidth=1.5)
        
    plt.title("Rolling 90-Day Sharpe Ratio Over Time (2022–2026)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Date", fontsize=11, labelpad=10)
    plt.ylabel("Rolling Sharpe Ratio (Annualized)", fontsize=11, labelpad=10)
    plt.legend(title="Key Mutual Funds", title_fontsize='11', loc='upper left', frameon=True, shadow=True)
    plt.tight_layout()
    
    rolling_sharpe_path = os.path.join(CHARTS_DIR, "rolling_sharpe_chart.png")
    plt.savefig(rolling_sharpe_path, dpi=150)
    plt.close()
    print(f"Saved Rolling Sharpe Chart to {rolling_sharpe_path}")
    
    # ----------------------------------------------------
    # Cohort Analysis
    # ----------------------------------------------------
    df_tx = pd.read_sql_query("SELECT investor_id, transaction_date, amfi_code, transaction_type, amount_inr FROM fact_transactions", conn)
    df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
    
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
        
        buy_group = group[group['transaction_type'].isin(['SIP', 'Lumpsum'])]
        fund_amounts = buy_group.groupby('amfi_code')['amount_inr'].sum().reset_index()
        if len(fund_amounts) > 0:
            top_fund_code = fund_amounts.sort_values(by='amount_inr', ascending=False).iloc[0]['amfi_code']
            top_fund_name = df_funds[df_funds['amfi_code'] == top_fund_code]['scheme_name'].iloc[0]
            top_fund_amt = fund_amounts.sort_values(by='amount_inr', ascending=False).iloc[0]['amount_inr']
        else:
            top_fund_name, top_fund_amt = "N/A", 0
            
        fund_counts = buy_group.groupby('amfi_code').size().reset_index(name='count')
        if len(fund_counts) > 0:
            top_count_code = fund_counts.sort_values(by='count', ascending=False).iloc[0]['amfi_code']
            top_count_name = df_funds[df_funds['amfi_code'] == top_count_code]['scheme_name'].iloc[0]
            top_count_val = fund_counts.sort_values(by='count', ascending=False).iloc[0]['count']
        else:
            top_count_name, top_count_val = "N/A", 0
            
        cohort_results.append({
            "Cohort Year": cohort_year,
            "Total Investors": group['investor_id'].nunique(),
            "Avg SIP Amount (Rs.)": avg_sip,
            "Gross Invested (Rs.)": gross_invested,
            "Net Invested (Rs.)": net_invested,
            "Top Fund (By Amount)": top_fund_name,
            "Top Fund Amount (Rs.)": top_fund_amt,
            "Top Fund (By Count)": top_count_name,
            "Top Fund Transaction Count": top_count_val
        })
        
    df_cohort = pd.DataFrame(cohort_results)
    cohort_path = os.path.join(PROCESSED_DIR, "cohort_analysis.csv")
    df_cohort.to_csv(cohort_path, index=False)
    print(f"Saved Cohort Analysis to {cohort_path}")
    
    # ----------------------------------------------------
    # SIP Continuity
    # ----------------------------------------------------
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
    continuity_path = os.path.join(PROCESSED_DIR, "sip_continuity.csv")
    investor_gaps.to_csv(continuity_path, index=False)
    print(f"Saved SIP Continuity Analysis to {continuity_path}")
    
    # Plot average gap distribution
    plt.figure(figsize=(10, 5))
    sns.histplot(investor_gaps['avg_gap'], bins=30, kde=True, color='teal')
    plt.title("Distribution of Average SIP Gaps (Days) per Investor", fontsize=12, fontweight='bold')
    plt.xlabel("Average Gap (Days)")
    plt.ylabel("Investor Count")
    plt.axvline(35, color='red', linestyle='--', label='At-Risk Threshold (35 days)')
    plt.legend()
    plt.tight_layout()
    
    gap_chart_path = os.path.join(CHARTS_DIR, "sip_gaps_distribution.png")
    plt.savefig(gap_chart_path, dpi=150)
    plt.close()
    print(f"Saved SIP Gaps Distribution Chart to {gap_chart_path}")
    
    # ----------------------------------------------------
    # Sector HHI
    # ----------------------------------------------------
    df_portfolio = pd.read_sql_query("SELECT amfi_code, stock_symbol, stock_name, sector, weight_pct FROM fact_portfolio", conn)
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
    
    hhi_path = os.path.join(PROCESSED_DIR, "sector_hhi.csv")
    df_hhi.to_csv(hhi_path, index=False)
    print(f"Saved Sector HHI Concentration to {hhi_path}")
    
    plt.figure(figsize=(12, 6.5))
    sns.barplot(data=df_hhi.head(15), x='hhi_percentage', y='scheme_name', palette='Reds_r')
    plt.title("Top 15 Most Concentrated Equity Funds by Sector HHI", fontsize=13, fontweight='bold')
    plt.xlabel("Sector HHI (Percentage Scale)")
    plt.ylabel("Scheme Name")
    plt.tight_layout()
    
    hhi_chart_path = os.path.join(CHARTS_DIR, "sector_hhi_concentration.png")
    plt.savefig(hhi_chart_path, dpi=150)
    plt.close()
    print(f"Saved Sector HHI Concentration Chart to {hhi_chart_path}")
    
    conn.close()
    print("=" * 60)
    print("PERFORMANCE & RISK CALCULATIONS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    run_performance_calculations()
