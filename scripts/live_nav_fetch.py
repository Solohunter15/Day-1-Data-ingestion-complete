"""
Bluestock Mutual Fund Analytics Platform - Live NAV Ingestion Ingests live NAV data from mfapi.in for selected mutual fund schemes
and saves the raw responses to the raw data directory.
"""

import os
import time
import requests
import pandas as pd

# Set up paths relative to the script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# Selected mutual fund schemes to fetch
SCHEMES = {
    "125497": "hdfc_top_100_direct_nav",
    "119551": "sbi_bluechip_nav",
    "120503": "icici_bluechip_nav",
    "118632": "nippon_large_cap_nav",
    "119092": "axis_bluechip_nav",
    "120841": "kotak_bluechip_nav"
}

def fetch_and_save_scheme(scheme_code: str, scheme_name: str) -> bool:
    """
    Fetches historical NAV for a specific scheme from mfapi.in and saves it as CSV.
    
    Args:
        scheme_code (str): The AMFI unique scheme identifier.
        scheme_name (str): Standard name used to name the output CSV file.
        
    Returns:
        bool: True if fetch and save was successful, False otherwise.
    """
    print(f"Fetching live data for Scheme Code: {scheme_code} ({scheme_name})...")
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "data" not in data or not data["data"]:
            print(f"Warning: No NAV data found for scheme {scheme_code}")
            return False
        
        # Extract metadata
        meta = data.get("meta", {})
        fund_house = meta.get("fund_house", "Unknown")
        scheme_type = meta.get("scheme_type", "Unknown")
        scheme_category = meta.get("scheme_category", "Unknown")
        scheme_official_name = meta.get("scheme_name", "Unknown")
        
        # Convert records to DataFrame
        nav_records = data.get("data", [])
        df = pd.DataFrame(nav_records)
        
        # Enrich with metadata
        df["scheme_code"] = scheme_code
        df["scheme_name"] = scheme_official_name
        df["fund_house"] = fund_house
        df["scheme_type"] = scheme_type
        df["scheme_category"] = scheme_category
        
        # Reorder columns
        df = df[["date", "nav", "scheme_code", "scheme_name", "fund_house", "scheme_type", "scheme_category"]]
        
        # Save output
        output_file = os.path.join(RAW_DIR, f"{scheme_name}.csv")
        df.to_csv(output_file, index=False)
        print(f"Success! Saved {len(df)} records to {output_file}\n")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching scheme {scheme_code}: {e}\n")
        return False

def main():
    """
    Main entrypoint for live NAV ingestion script.
    """
    print("=" * 60)
    print("STARTING LIVE NAV INGESTION (mfapi.in)")
    print("=" * 60)
    
    success_count = 0
    for code, name in SCHEMES.items():
        if fetch_and_save_scheme(code, name):
            success_count += 1
        # Be polite to the free API
        time.sleep(1)
        
    print("=" * 60)
    print(f"NAV INGESTION COMPLETE. Successfully fetched {success_count}/{len(SCHEMES)} schemes.")
    print("=" * 60)

if __name__ == "__main__":
    main()
