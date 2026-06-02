import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Paths setup
RAW_DIR = r"C:\Users\jibum\OneDrive\Desktop\Bluestock Internship\data\raw"
os.makedirs(RAW_DIR, exist_ok=True)

# File names of the 10 CSV datasets
CSV_FILES = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

def generate_synthetic_data():
    """Bypassed: Using actual raw data files provided in the data/raw directory."""
    print("=" * 60)
    print("USING PROVIDED REAL-WORLD DATASETS IN RAW FOLDER")
    print("=" * 60)




def load_and_inspect_datasets():
    print("=" * 60)
    print("LOADING AND INSPECTING DATASETS")
    print("=" * 60)
    
    anomalies = {}
    
    for filename in CSV_FILES:
        path = os.path.join(RAW_DIR, filename)
        print("\n" + "=" * 50)
        print(f"FILE: {filename}")
        
        try:
            df = pd.read_csv(path)
            
            # Print Shape, Dtypes, Head
            print(f"Shape: {df.shape}")
            print("\nDtypes:")
            print(df.dtypes)
            print("\nHead Preview:")
            print(df.head(3))
            
            # Note anomalies
            file_anomalies = []
            
            # 1. Null values check
            null_counts = df.isnull().sum()
            null_cols = null_counts[null_counts > 0]
            if len(null_cols) > 0:
                print("\n[ANOMALY] Missing Values Found:")
                print(null_counts[null_counts > 0])
                for col, count in null_cols.items():
                    file_anomalies.append(f"{count} null values in '{col}'")
            
            # 2. Duplicate rows check
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                print(f"\n[ANOMALY] Duplicated Rows: {duplicates}")
                file_anomalies.append(f"{duplicates} duplicate rows detected")
                
            # 3. Date columns loaded as object instead of datetime
            for col in df.columns:
                if "date" in col.lower() and df[col].dtype == "object":
                    print(f"\n[ANOMALY] Date Column Loaded as Object: '{col}'")
                    file_anomalies.append(f"Date column '{col}' is loaded as object (string)")
            
            if file_anomalies:
                anomalies[filename] = file_anomalies
                
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            anomalies[filename] = [f"Critical Load Error: {e}"]
            
    print("\n" + "=" * 60)
    print("SUMMARY OF DETECTED ANOMALIES")
    print("=" * 60)
    for file, anomaly_list in anomalies.items():
        print(f"\n* {file}:")
        for item in anomaly_list:
            print(f"  - {item}")
    print("=" * 60 + "\n")


def explore_fund_master():
    print("=" * 60)
    print("EXPLORING FUND MASTER DIMENSIONS")
    print("=" * 60)
    
    path = os.path.join(RAW_DIR, "01_fund_master.csv")
    if not os.path.exists(path):
        print("Error: 01_fund_master.csv does not exist.")
        return
        
    df = pd.read_csv(path)
    
    # 1. Unique Dimensions
    print("Unique Fund Houses:")
    print(df["fund_house"].dropna().unique())
    print("\nUnique Categories:")
    print(df["category"].dropna().unique())
    print("\nUnique Sub-Categories:")
    print(df["sub_category"].dropna().unique())
    print("\nUnique Risk Categories:")
    print(df["risk_category"].dropna().unique())
    
    # 2. Understanding AMFI Scheme Code Structure
    print("\n" + "=" * 50)
    print("AMFI SCHEME CODE STRUCTURE UNDERSTANDING")
    print("=" * 50)
    print("The AMFI (Association of Mutual Funds in India) Code is a unique 5-6 digit identifier")
    print("assigned to each mutual fund scheme. Key architectural highlights include:")
    print("1. Key Join Field: Acts as the primary key/unique identifier to link fund static attributes")
    print("   (like category, AMC, exit loads) with dynamic transaction or daily NAV time series.")
    print("2. Standardization: Standardizes scheme tracking across the industry, preventing conflicts")
    print("   caused by naming variations across platforms.")
    print("3. Query Performance: As a numeric string, it optimizes database joins and index lookups.")
    print("=" * 50 + "\n")


def validate_amfi_codes():
    print("=" * 60)
    print("VALIDATING AMFI CODES CONSISTENCY")
    print("=" * 60)
    
    master_path = os.path.join(RAW_DIR, "01_fund_master.csv")
    nav_path = os.path.join(RAW_DIR, "02_nav_history.csv")
    
    if not os.path.exists(master_path) or not os.path.exists(nav_path):
        print("Error: Missing required files for AMFI validation.")
        return
        
    df_master = pd.read_csv(master_path)
    df_nav = pd.read_csv(nav_path)
    
    # Extract unique codes as cleaned string sets
    master_codes = set(df_master["amfi_code"].dropna().astype(str).str.strip())
    nav_codes = set(df_nav["amfi_code"].dropna().astype(str).str.strip())
    
    # Identical codes checking
    missing_in_nav = master_codes - nav_codes
    extra_in_nav = nav_codes - master_codes
    
    print(f"Total Unique AMFI Codes in Fund Master: {len(master_codes)}")
    print(f"Total Unique AMFI Codes in NAV History: {len(nav_codes)}")
    
    print("\nIntegrity Checking Details:")
    if len(missing_in_nav) == 0:
        print("[SUCCESS] Every AMFI code in fund_master exists in nav_history.")
    else:
        print(f"[WARNING] {len(missing_in_nav)} codes in fund_master are missing in nav_history.")
        print(f"  Missing codes: {missing_in_nav}")
        
    if len(extra_in_nav) > 0:
        print(f"[INFO] Found {len(extra_in_nav)} codes in nav_history that are not in fund_master.")
        print(f"  Extra codes: {extra_in_nav}")
        
    print("=" * 60 + "\n")


def main():
    # Step 1: Generate synthetic raw data if not present
    generate_synthetic_data()
    
    # Step 2: Load and inspect shapes, dtypes, and anomalies
    load_and_inspect_datasets()
    
    # Step 3: Explore dimensions and structural highlights
    explore_fund_master()
    
    # Step 4: Validate AMFI relational integrity
    validate_amfi_codes()

if __name__ == "__main__":
    main()
