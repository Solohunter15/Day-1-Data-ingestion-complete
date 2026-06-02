import os
import requests
import pandas as pd
import time

# Create directories if they do not exist
RAW_DIR = r"C:\Users\jibum\OneDrive\Desktop\Bluestock Internship\data\raw"
os.makedirs(RAW_DIR, exist_ok=True)

# List of schemes to fetch
schemes = {
    "125497": "hdfc_top_100_direct_nav",
    "119551": "sbi_bluechip_nav",
    "120503": "icici_bluechip_nav",
    "118632": "nippon_large_cap_nav",
    "119092": "axis_bluechip_nav",
    "120841": "kotak_bluechip_nav"
}

def fetch_and_save_scheme(scheme_code, scheme_name):
    print(f"Fetching data for Scheme Code: {scheme_code} ({scheme_name})...")
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
        
        # Convert daily NAV records to DataFrame
        nav_records = data.get("data", [])
        df = pd.DataFrame(nav_records)
        
        # Add metadata columns
        df["scheme_code"] = scheme_code
        df["scheme_name"] = scheme_official_name
        df["fund_house"] = fund_house
        df["scheme_type"] = scheme_type
        df["scheme_category"] = scheme_category
        
        # Rearrange columns
        df = df[["date", "nav", "scheme_code", "scheme_name", "fund_house", "scheme_type", "scheme_category"]]
        
        # Save as CSV
        output_file = os.path.join(RAW_DIR, f"{scheme_name}.csv")
        df.to_csv(output_file, index=False)
        print(f"Success! Saved {len(df)} records to {output_file}\n")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching scheme {scheme_code}: {e}\n")
        return False

def main():
    print("=" * 60)
    print("STARTING LIVE NAV INGESTION (mfapi.in)")
    print("=" * 60)
    
    success_count = 0
    for code, name in schemes.items():
        if fetch_and_save_scheme(code, name):
            success_count += 1
        # Polite delay to be kind to the free API
        time.sleep(1)
        
    print("=" * 60)
    print(f"NAV INGESTION COMPLETE. Successfully fetched {success_count}/{len(schemes)} schemes.")
    print("=" * 60)

if __name__ == "__main__":
    main()
