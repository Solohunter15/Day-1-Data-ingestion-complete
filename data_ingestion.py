import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Paths setup
RAW_DIR = r"C:\Users\jibum\OneDrive\Desktop\Bluestock Internship\data\raw"
os.makedirs(RAW_DIR, exist_ok=True)

# File names of the 10 CSV datasets
CSV_FILES = [
    "fund_master.csv",
    "nav_history.csv",
    "investors.csv",
    "transactions.csv",
    "fund_managers.csv",
    "portfolio_holdings.csv",
    "amc_details.csv",
    "expense_ratios.csv",
    "benchmarks.csv",
    "benchmark_history.csv"
]

def generate_synthetic_data():
    """Generates highly realistic mutual fund data files in data/raw if they are missing."""
    print("=" * 60)
    print("GENERATING SYNTHETIC DATASETS (Bootstrapping local ETL)")
    print("=" * 60)
    
    # 1. Fund Master
    fund_master_path = os.path.join(RAW_DIR, "fund_master.csv")
    if not os.path.exists(fund_master_path):
        schemes = [
            {"amfi_code": "125497", "scheme_name": "HDFC Top 100 Fund - Direct Plan", "fund_house": "HDFC Mutual Fund", "category": "Equity", "sub_category": "Large Cap", "risk_grade": "Very High"},
            {"amfi_code": "119551", "scheme_name": "SBI Bluechip Fund - Direct Plan", "fund_house": "SBI Mutual Fund", "category": "Equity", "sub_category": "Large Cap", "risk_grade": "High"},
            {"amfi_code": "120503", "scheme_name": "ICICI Prudential Bluechip Fund - Direct Plan", "fund_house": "ICICI Prudential Mutual Fund", "category": "Equity", "sub_category": "Large Cap", "risk_grade": "High"},
            {"amfi_code": "118632", "scheme_name": "Nippon India Large Cap Fund - Direct Plan", "fund_house": "Nippon India Mutual Fund", "category": "Equity", "sub_category": "Large Cap", "risk_grade": "Very High"},
            {"amfi_code": "119092", "scheme_name": "Axis Bluechip Fund - Direct Plan", "fund_house": "Axis Mutual Fund", "category": "Equity", "sub_category": "Large Cap", "risk_grade": "High"},
            {"amfi_code": "120841", "scheme_name": "Kotak Bluechip Fund - Direct Plan", "fund_house": "Kotak Mahindra Mutual Fund", "category": "Equity", "sub_category": "Large Cap", "risk_grade": "High"},
            # Extra schemes for rich dataset
            {"amfi_code": "148918", "scheme_name": "Parag Parikh Flexi Cap Fund - Direct Plan", "fund_house": "PPFAS Mutual Fund", "category": "Equity", "sub_category": "Flexi Cap", "risk_grade": "Very High"},
            {"amfi_code": "119775", "scheme_name": "SBI Magnum Midcap Fund - Direct Plan", "fund_house": "SBI Mutual Fund", "category": "Equity", "sub_category": "Mid Cap", "risk_grade": "Very High"},
            {"amfi_code": "120716", "scheme_name": "HDFC Mid-Cap Opportunities Fund - Direct Plan", "fund_house": "HDFC Mutual Fund", "category": "Equity", "sub_category": "Mid Cap", "risk_grade": "Very High"},
            {"amfi_code": "118778", "scheme_name": "Nippon India Small Cap Fund - Direct Plan", "fund_house": "Nippon India Mutual Fund", "category": "Equity", "sub_category": "Small Cap", "risk_grade": "Very High"},
            # Introduce anomaly: AMFI code missing in nav_history
            {"amfi_code": "999999", "scheme_name": "Test Missing NAV Fund", "fund_house": "Ghost Mutual Fund", "category": "Debt", "sub_category": "Liquid", "risk_grade": None}, # Null risk_grade
            # Introduce anomaly: Duplicate entry
            {"amfi_code": "125497", "scheme_name": "HDFC Top 100 Fund - Direct Plan", "fund_house": "HDFC Mutual Fund", "category": "Equity", "sub_category": "Large Cap", "risk_grade": "Very High"}
        ]
        pd.DataFrame(schemes).to_csv(fund_master_path, index=False)
        print("Generated fund_master.csv (with intentional nulls and duplicates)")

    # 2. NAV History
    nav_history_path = os.path.join(RAW_DIR, "nav_history.csv")
    if not os.path.exists(nav_history_path):
        nav_data = []
        codes = ["125497", "119551", "120503", "118632", "119092", "120841", "148918", "119775", "120716", "118778"]
        base_navs = {"125497": 110.0, "119551": 85.0, "120503": 92.0, "118632": 78.0, "119092": 60.0, "120841": 55.0, "148918": 68.0, "119775": 170.0, "120716": 150.0, "118778": 140.0}
        
        # 10 days of historical data for each scheme
        end_date = datetime.now()
        for code in codes:
            current_nav = base_navs[code]
            for i in range(10):
                date_str = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
                # Introduce date format anomaly for one entry
                if code == "119551" and i == 5:
                    date_str = (end_date - timedelta(days=i)).strftime("%d/%m/%Y")
                
                # Daily variation
                current_nav += np.random.uniform(-1.5, 1.8)
                nav_data.append({
                    "amfi_code": code,
                    "date": date_str,
                    "nav": round(current_nav, 4)
                })
        
        # Add an extra AMFI code in nav_history not in fund_master
        nav_data.append({"amfi_code": "888888", "date": end_date.strftime("%Y-%m-%d"), "nav": 42.5000})
        
        pd.DataFrame(nav_data).to_csv(nav_history_path, index=False)
        print("Generated nav_history.csv (with mismatched codes and mixed dates)")

    # 3. Investors
    investors_path = os.path.join(RAW_DIR, "investors.csv")
    if not os.path.exists(investors_path):
        investors = [
            {"investor_id": "INV001", "name": "Jibu Mathew", "email": "jibu@example.com", "risk_profile": "Aggressive", "joined_date": "2024-01-15"},
            {"investor_id": "INV002", "name": "Anurag Kaushik", "email": "anurag@example.com", "risk_profile": "Moderate", "joined_date": "2024-02-10"},
            {"investor_id": "INV003", "name": "Anshuman Maity", "email": "anshuman@example.com", "risk_profile": "Conservative", "joined_date": "2024-03-01"},
            {"investor_id": "INV004", "name": "Bharath V", "email": None, "risk_profile": "Aggressive", "joined_date": "2024-03-12"}, # Null email
            {"investor_id": "INV005", "name": "Sarah Smith", "email": "sarah@example.com", "risk_profile": "Moderate", "joined_date": "2024-04-05"}
        ]
        pd.DataFrame(investors).to_csv(investors_path, index=False)
        print("Generated investors.csv")

    # 4. Transactions
    transactions_path = os.path.join(RAW_DIR, "transactions.csv")
    if not os.path.exists(transactions_path):
        transactions = [
            {"transaction_id": "TXN1001", "investor_id": "INV001", "amfi_code": "125497", "transaction_type": "BUY", "amount": 50000.0, "units": 454.54, "transaction_date": "2025-05-15"},
            {"transaction_id": "TXN1002", "investor_id": "INV002", "amfi_code": "119551", "transaction_type": "BUY", "amount": 25000.0, "units": 294.11, "transaction_date": "2025-05-16"},
            {"transaction_id": "TXN1003", "investor_id": "INV003", "amfi_code": "120503", "transaction_type": "BUY", "amount": 10000.0, "units": 108.69, "transaction_date": "2025-05-17"},
            {"transaction_id": "TXN1004", "investor_id": "INV004", "amfi_code": "148918", "transaction_type": "BUY", "amount": 100000.0, "units": None, "transaction_date": "2025-05-18"}, # Null units
            {"transaction_id": "TXN1005", "investor_id": "INV001", "amfi_code": "118778", "transaction_type": "BUY", "amount": 15000.0, "units": 107.14, "transaction_date": "2025-05-19"},
            # Duplicate transaction row
            {"transaction_id": "TXN1001", "investor_id": "INV001", "amfi_code": "125497", "transaction_type": "BUY", "amount": 50000.0, "units": 454.54, "transaction_date": "2025-05-15"}
        ]
        pd.DataFrame(transactions).to_csv(transactions_path, index=False)
        print("Generated transactions.csv")

    # 5. Fund Managers
    fund_managers_path = os.path.join(RAW_DIR, "fund_managers.csv")
    if not os.path.exists(fund_managers_path):
        managers = [
            {"manager_id": "MGR01", "name": "Milind Bafna", "experience_years": 18, "qualification": "CFA, MBA"},
            {"manager_id": "MGR02", "name": "R. Srinivasan", "experience_years": 22, "qualification": "M.Com, CFA"},
            {"manager_id": "MGR03", "name": "Sankaran Naren", "experience_years": 25, "qualification": "B.Tech, MBA"},
            {"manager_id": "MGR04", "name": "Rajeev Thakkar", "experience_years": 20, "qualification": "B.Com, CA, CFA"}
        ]
        pd.DataFrame(managers).to_csv(fund_managers_path, index=False)
        print("Generated fund_managers.csv")

    # 6. Portfolio Holdings
    portfolio_holdings_path = os.path.join(RAW_DIR, "portfolio_holdings.csv")
    if not os.path.exists(portfolio_holdings_path):
        holdings = [
            {"holding_id": "HLD5001", "amfi_code": "125497", "stock_name": "HDFC Bank Ltd.", "sector": "Financial Services", "allocation_percentage": 9.2},
            {"holding_id": "HLD5002", "amfi_code": "125497", "stock_name": "Reliance Industries Ltd.", "sector": "Oil & Gas", "allocation_percentage": 8.5},
            {"holding_id": "HLD5003", "amfi_code": "119551", "stock_name": "ICICI Bank Ltd.", "sector": "Financial Services", "allocation_percentage": 7.8},
            {"holding_id": "HLD5004", "amfi_code": "119551", "stock_name": "Infosys Ltd.", "sector": "Information Technology", "allocation_percentage": 6.2},
            {"holding_id": "HLD5005", "amfi_code": "148918", "stock_name": "Alphabet Inc.", "sector": "Technology", "allocation_percentage": 5.4}
        ]
        pd.DataFrame(holdings).to_csv(portfolio_holdings_path, index=False)
        print("Generated portfolio_holdings.csv")

    # 7. AMC Details
    amc_details_path = os.path.join(RAW_DIR, "amc_details.csv")
    if not os.path.exists(amc_details_path):
        amcs = [
            {"amc_id": "AMC01", "fund_house": "HDFC Mutual Fund", "ceo": "Navneet Munot", "aum_in_crores": 550000, "establishment_year": 1999},
            {"amc_id": "AMC02", "fund_house": "SBI Mutual Fund", "ceo": "Shamsher Singh", "aum_in_crores": 820000, "establishment_year": 1987},
            {"amc_id": "AMC03", "fund_house": "ICICI Prudential Mutual Fund", "ceo": "Nimesh Shah", "aum_in_crores": 610000, "establishment_year": 1993},
            {"amc_id": "AMC04", "fund_house": "Nippon India Mutual Fund", "ceo": "Sundeep Sikka", "aum_in_crores": 380000, "establishment_year": 1995}
        ]
        pd.DataFrame(amcs).to_csv(amc_details_path, index=False)
        print("Generated amc_details.csv")

    # 8. Expense Ratios
    expense_ratios_path = os.path.join(RAW_DIR, "expense_ratios.csv")
    if not os.path.exists(expense_ratios_path):
        ratios = [
            {"amfi_code": "125497", "expense_ratio": 0.85, "exit_load": 1.00, "turnover_ratio": 24.5},
            {"amfi_code": "119551", "expense_ratio": 0.92, "exit_load": 1.00, "turnover_ratio": 18.2},
            {"amfi_code": "120503", "expense_ratio": 0.78, "exit_load": 1.00, "turnover_ratio": 32.1},
            {"amfi_code": "148918", "expense_ratio": 0.65, "exit_load": 2.00, "turnover_ratio": 8.5}
        ]
        pd.DataFrame(ratios).to_csv(expense_ratios_path, index=False)
        print("Generated expense_ratios.csv")

    # 9. Benchmarks
    benchmarks_path = os.path.join(RAW_DIR, "benchmarks.csv")
    if not os.path.exists(benchmarks_path):
        benchmarks = [
            {"benchmark_id": "BM01", "benchmark_name": "NIFTY 50", "index_type": "Large Cap"},
            {"benchmark_id": "BM02", "benchmark_name": "NIFTY Next 50", "index_type": "Large Cap"},
            {"benchmark_id": "BM03", "benchmark_name": "NIFTY Midcap 150", "index_type": "Mid Cap"},
            {"benchmark_id": "BM04", "benchmark_name": "NIFTY Smallcap 250", "index_type": "Small Cap"}
        ]
        pd.DataFrame(benchmarks).to_csv(benchmarks_path, index=False)
        print("Generated benchmarks.csv")

    # 10. Benchmark History
    benchmark_history_path = os.path.join(RAW_DIR, "benchmark_history.csv")
    if not os.path.exists(benchmark_history_path):
        bm_history = []
        end_date = datetime.now()
        for i in range(10):
            date_str = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            bm_history.append({"benchmark_id": "BM01", "date": date_str, "index_value": round(22500 + i * 15.5, 2)})
            bm_history.append({"benchmark_id": "BM03", "date": date_str, "index_value": round(15000 - i * 8.2, 2)})
        pd.DataFrame(bm_history).to_csv(benchmark_history_path, index=False)
        print("Generated benchmark_history.csv")
        
    print("=" * 60)
    print("BOOTSTRAPPING COMPLETE. All 10 raw datasets created.\n")


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
    
    path = os.path.join(RAW_DIR, "fund_master.csv")
    if not os.path.exists(path):
        print("Error: fund_master.csv does not exist.")
        return
        
    df = pd.read_csv(path)
    
    # 1. Unique Dimensions
    print("Unique Fund Houses:")
    print(df["fund_house"].dropna().unique())
    print("\nUnique Categories:")
    print(df["category"].dropna().unique())
    print("\nUnique Sub-Categories:")
    print(df["sub_category"].dropna().unique())
    print("\nUnique Risk Grades:")
    print(df["risk_grade"].dropna().unique())
    
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
    
    master_path = os.path.join(RAW_DIR, "fund_master.csv")
    nav_path = os.path.join(RAW_DIR, "nav_history.csv")
    
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
