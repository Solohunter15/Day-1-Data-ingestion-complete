import sqlite3
import pandas as pd
import sys
import argparse

def recommend_funds(risk_appetite):
    db_path = 'data/db/bluestock_mf.db'
    
    # Map input risk appetite to database risk_grade values
    risk_appetite = risk_appetite.strip().lower()
    
    if risk_appetite == 'low':
        target_grades = ['Low']
    elif risk_appetite == 'moderate':
        target_grades = ['Moderate', 'Moderately High']
    elif risk_appetite == 'high':
        target_grades = ['High', 'Very High']
    else:
        # If it doesn't match low/moderate/high, try matching the database categories directly
        capitalized = risk_appetite.title()
        if capitalized in ['Low', 'Moderate', 'Moderately High', 'High', 'Very High']:
            target_grades = [capitalized]
        else:
            print(f"Error: Invalid risk appetite '{risk_appetite}'. Please choose from: Low, Moderate, High.")
            return None

    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        print(f"Error connecting to database at {db_path}: {e}")
        return None

    # Query matching funds from fact_performance
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

    # Select top 3 funds
    top_3 = df.head(3)
    return top_3

def main():
    parser = argparse.ArgumentParser(description="Bluestock Mutual Fund Recommender")
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
        print("\n" + "=" * 80)
        print(f" TOP 3 RECOMMENDATIONS FOR {risk_input.upper()} RISK APPETITE")
        print("=" * 80)
        
        # Format for pretty printing
        headers = ["Rank", "AMFI Code", "Scheme Name", "Category", "Risk Grade", "Sharpe Ratio", "3-Yr CAGR (%)"]
        print(f"{headers[0]:<5} | {headers[1]:<10} | {headers[2]:<45} | {headers[3]:<10} | {headers[4]:<15} | {headers[5]:<12} | {headers[6]:<13}")
        print("-" * 130)
        for idx, row in top_funds.iterrows():
            rank = idx + 1
            name_truncated = row['scheme_name'][:45]
            print(f"{rank:<5} | {row['amfi_code']:<10} | {name_truncated:<45} | {row['category']:<10} | {row['risk_grade']:<15} | {row['sharpe_ratio']:<12.4f} | {row['return_3yr_pct']:<13.2f}%")
        print("=" * 80)
    elif top_funds is not None:
        print("No recommendations available.")

if __name__ == '__main__':
    main()
