"""
Bluestock Mutual Fund Analytics Platform - ETL Pipeline
Cleans raw CSV files, executes the schema DDL to create tables, and loads
the clean datasets into the SQLite database.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

# Set up paths relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
DB_DIR = os.path.join(PROJECT_ROOT, "data", "db")
DB_PATH = os.path.join(DB_DIR, "bluestock_mf.db")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "sql", "schema.sql")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

def clean_fund_master():
    """Cleans 01_fund_master.csv by removing duplicate scheme records."""
    print("Cleaning 01_fund_master.csv...")
    path = os.path.join(RAW_DIR, "01_fund_master.csv")
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset=["amfi_code"])
    out_path = os.path.join(PROCESSED_DIR, "01_fund_master.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved cleaned Fund Master: {df.shape} to {out_path}\n")

def clean_nav_history():
    """
    Cleans 02_nav_history.csv:
    - Parses dates
    - Validates NAV > 0
    - Removes duplicate records (amfi_code + date)
    - Reindexes and forward-fills holidays/weekends per fund to prevent return distortion
    """
    print("Cleaning 02_nav_history.csv...")
    path = os.path.join(RAW_DIR, "02_nav_history.csv")
    df = pd.read_csv(path)
    
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["nav"] > 0]
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    
    cleaned_navs = []
    for code, group in df.groupby("amfi_code"):
        group = group.sort_values("date").set_index("date")
        min_date = group.index.min()
        max_date = group.index.max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq="D")
        
        group = group.reindex(all_dates)
        group["amfi_code"] = code
        group["nav"] = group["nav"].ffill()
        
        group = group.reset_index().rename(columns={"index": "date"})
        cleaned_navs.append(group)
        
    df_cleaned = pd.concat(cleaned_navs, ignore_index=True)
    df_cleaned["date"] = df_cleaned["date"].dt.strftime("%Y-%m-%d")
    
    out_path = os.path.join(PROCESSED_DIR, "02_nav_history.csv")
    df_cleaned.to_csv(out_path, index=False)
    print(f"Saved forward-filled NAV history: {df_cleaned.shape} to {out_path}\n")

def clean_investor_transactions():
    """Cleans 08_investor_transactions.csv: standardizes type and KYC, validates amount."""
    print("Cleaning 08_investor_transactions.csv...")
    path = os.path.join(RAW_DIR, "08_investor_transactions.csv")
    df = pd.read_csv(path)
    
    df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.strftime("%Y-%m-%d")
    
    type_map = {
        "sip": "SIP", "SIP": "SIP",
        "lumpsum": "Lumpsum", "Lumpsum": "Lumpsum",
        "redemption": "Redemption", "Redemption": "Redemption"
    }
    df["transaction_type"] = df["transaction_type"].map(type_map).fillna("SIP")
    df = df[df["amount_inr"] > 0]
    
    kyc_map = {
        "verified": "Verified", "Verified": "Verified",
        "pending": "Pending", "Pending": "Pending"
    }
    df["kyc_status"] = df["kyc_status"].map(kyc_map).fillna("Verified")
    
    out_path = os.path.join(PROCESSED_DIR, "08_investor_transactions.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved cleaned Transactions: {df.shape} to {out_path}\n")

def clean_scheme_performance():
    """Cleans 07_scheme_performance.csv: coerces columns to numeric, validates expense ratio."""
    print("Cleaning 07_scheme_performance.csv...")
    path = os.path.join(RAW_DIR, "07_scheme_performance.csv")
    df = pd.read_csv(path)
    
    numeric_cols = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", 
        "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", 
        "sortino_ratio", "expense_ratio_pct"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    invalid_expense = df[(df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)]
    if len(invalid_expense) > 0:
        print(f"[WARNING] Found {len(invalid_expense)} records with expense ratio out of bounds (0.1% - 2.5%).")
        
    out_path = os.path.join(PROCESSED_DIR, "07_scheme_performance.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved cleaned Scheme Performance: {df.shape} to {out_path}\n")

def copy_clean_others():
    """Copies other raw files to processed folder, filling in basic NaNs where appropriate."""
    others = [
        "03_aum_by_fund_house.csv",
        "04_monthly_sip_inflows.csv",
        "05_category_inflows.csv",
        "06_industry_folio_count.csv",
        "09_portfolio_holdings.csv",
        "10_benchmark_indices.csv"
    ]
    
    for filename in others:
        print(f"Processing and copying {filename}...")
        path = os.path.join(RAW_DIR, filename)
        df = pd.read_csv(path)
        
        if filename == "04_monthly_sip_inflows.csv":
            df["yoy_growth_pct"] = df["yoy_growth_pct"].fillna(0.0)
            
        out_path = os.path.join(PROCESSED_DIR, filename)
        df.to_csv(out_path, index=False)
        print(f"Saved {filename}: {df.shape} to {out_path}\n")

def execute_ddl():
    """Executes the DDL statements in schema.sql to create the database tables."""
    print("Executing schema DDL script to create SQLite tables...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(SCHEMA_PATH, "r") as f:
        sql_script = f.read()
        
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("Database tables and indexes created successfully.\n")

def populate_date_dimension():
    """Generates dates between 2022-01-01 and 2026-12-31 and populates dim_date."""
    print("Generating and populating dim_date table...")
    dates = pd.date_range(start="2022-01-01", end="2026-12-31", freq="D")
    df_date = pd.DataFrame({"date": dates})
    
    df_date["year"] = df_date["date"].dt.year
    df_date["month"] = df_date["date"].dt.month
    df_date["quarter"] = df_date["date"].dt.quarter
    df_date["is_weekday"] = (df_date["date"].dt.dayofweek < 5).astype(int)
    
    df_date["date"] = df_date["date"].dt.strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_PATH)
    df_date.to_sql("dim_date", conn, if_exists="append", index=False)
    conn.close()
    print(f"Generated and loaded {len(df_date)} rows into dim_date.\n")

def load_table(csv_name: str, table_name: str, mapping: dict = None):
    """Loads a processed CSV file into the database."""
    csv_path = os.path.join(PROCESSED_DIR, csv_name)
    if not os.path.exists(csv_path):
        print(f"File {csv_name} not found, skipping.")
        return
        
    df = pd.read_csv(csv_path)
    
    if mapping:
        df = df.rename(columns=mapping)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = [col[1] for col in cursor.fetchall()]
    
    df_load = df[[c for c in df.columns if c in cols]]
    df_load.to_sql(table_name, conn, if_exists="append", index=False)
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    db_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"Loaded {csv_name} -> {table_name}: CSV rows={len(df)}, DB table rows={db_count}")

def main():
    """Executes the full ETL pipeline: cleaning and DB loading."""
    print("=" * 60)
    print("STARTING DATA CLEANING & ETL PIPELINE")
    print("=" * 60)
    
    # 1. Clean CSVs
    clean_fund_master()
    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    copy_clean_others()
    
    # 2. Database Loader
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Removed existing bluestock_mf.db for a clean run.")
        except Exception as e:
            print(f"Error removing existing database: {e}. Trying to truncate or continue.")
            
    execute_ddl()
    populate_date_dimension()
    
    # Load Tables
    load_table("01_fund_master.csv", "dim_fund")
    load_table("02_nav_history.csv", "fact_nav")
    load_table("08_investor_transactions.csv", "fact_transactions")
    load_table("07_scheme_performance.csv", "fact_performance")
    load_table("03_aum_by_fund_house.csv", "fact_aum")
    load_table("09_portfolio_holdings.csv", "fact_portfolio")
    load_table("04_monthly_sip_inflows.csv", "fact_sip_industry")
    
    print("=" * 60)
    print("ETL PIPELINE COMPLETE. Data cleaned and loaded to bluestock_mf.db successfully.")
    print("=" * 60)

if __name__ == "__main__":
    main()
