"""
Bluestock Mutual Fund Analytics Platform - Fund Recommender
A CLI tool that queries the SQLite database to recommend mutual funds
based on the investor's risk appetite (Low, Moderate, High).
"""

import os
import sys
import sqlite3
import argparse
import pandas as pd

# Set up paths relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "db", "bluestock_mf.db")

def recommend_funds(risk_appetite: str):
    """
    Queries the database and returns the top 3 mutual funds sorted by Sharpe ratio
    matching the specified risk appetite category.
    
    Args:
        risk_appetite (str): One of 'low', 'moderate', or 'high'.
        
    Returns:
        pd.DataFrame: A DataFrame of recommended funds, or None if database query fails.
    """
    risk_appetite = risk_appetite.strip().lower()
    
    # Map CLI risk appetite inputs to database risk grades
    if risk_appetite == 'low':
        target_grades = ['Low']
    elif risk_appetite == 'moderate':
        target_grades = ['Moderate', 'Moderately High']
    elif risk_appetite == 'high':
        target_grades = ['High', 'Very High']
    else:
        # Standardize for direct database match if not low/moderate/high
        capitalized = risk_appetite.title()
        if capitalized in ['Low', 'Moderate', 'Moderately High', 'High', 'Very High']:
            target_grades = [capitalized]
        else:
            print(f"Error: Invalid risk appetite '{risk_appetite}'. Please choose from: Low, Moderate, High.")
            return None

    if not os.path.exists(DB_PATH):
        print(f"Error: Relational database does not exist at {DB_PATH}. Please run the ETL pipeline first.")
        return None

    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"Error connecting to database at {DB_PATH}: {e}")
        return None

    # Query matching funds from fact_performance sorted by Sharpe Ratio descending
    placeholders = ', '.join(['?'] * len(target_grades))
    query = f"""
        SELECT amfi_code, scheme_name, category, plan, risk_grade, sharpe_ratio, return_3yr_pct
        FROM fact_performance
        WHERE risk_grade IN ({placeholders})
        ORDER BY sharpe_ratio DESC
    """
    
    try:
        df = pd.read_sql_query(query, conn, params=target_grades)
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.close()
        return None
        
    conn.close()

    if df.empty:
        print(f"No funds found for risk categories: {target_grades}")
        return df

    return df.head(3)

def main():
    """
    CLI Parser and interactive prompt handler for recommender.
    """
    parser = argparse.ArgumentParser(description="Bluestock Mutual Fund Recommender CLI Tool")
    parser.add_argument(
        'risk', 
        type=str, 
        nargs='?', 
        default=None, 
        help="Investor risk appetite: Low, Moderate, or High"
    )
    args = parser.parse_args()

    risk_input = args.risk
    if not risk_input:
        print("=== Bluestock Mutual Fund Recommender ===")
        print("Please choose your risk appetite from: Low, Moderate, High")
        try:
            risk_input = input("Enter risk appetite: ").strip()
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)

    if not risk_input:
        print("Error: Risk appetite input is empty.")
        sys.exit(1)

    top_funds = recommend_funds(risk_input)
    if top_funds is not None and not top_funds.empty:
        print("\n" + "=" * 130)
        print(f" TOP 3 RECOMMENDATIONS FOR {risk_input.upper()} RISK APPETITE (Sorted by Sharpe Ratio)")
        print("=" * 130)
        
        headers = ["Rank", "AMFI Code", "Scheme Name", "Category", "Risk Grade", "Sharpe Ratio", "3-Yr CAGR (%)"]
        print(f"{headers[0]:<5} | {headers[1]:<10} | {headers[2]:<45} | {headers[3]:<10} | {headers[4]:<15} | {headers[5]:<12} | {headers[6]:<13}")
        print("-" * 130)
        for idx, row in top_funds.reset_index(drop=True).iterrows():
            rank = idx + 1
            name_truncated = row['scheme_name'][:45]
            print(f"{rank:<5} | {row['amfi_code']:<10} | {name_truncated:<45} | {row['category']:<10} | {row['risk_grade']:<15} | {row['sharpe_ratio']:<12.4f} | {row['return_3yr_pct']:<13.2f}%")
        print("=" * 130 + "\n")
    elif top_funds is not None:
        print("No recommendations available.")

if __name__ == '__main__':
    main()
