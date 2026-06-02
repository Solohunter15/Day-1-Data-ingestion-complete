# Day 1 Data Ingestion & Quality Summary

Hey, 

Here is the complete summary of the work I did today for the Mutual Fund Analytics setup. I've got the project folder structure organized, the local environment set up, all the raw datasets ingested, and the live API connection working. 

I did a deep dive into the 10 CSV files to check for quality issues. There are a few dirty spots (duplicates, missing fields, and date format mismatches) that we will need to clean up first thing tomorrow. I’ve detailed everything below.

---

## 1. Project Directory & Environment Layout

I set up the project folder structure inside `C:\Users\jibum\OneDrive\Desktop\Bluestock Internship`. 

Here is the current layout and where we stand:
*   `data/raw/` - **Active**. This contains the 10 original local CSV datasets, plus the raw historical CSVs I downloaded from the API.
*   `data/processed/` - **Empty**. This is intentional! It is currently an empty staging folder. I will be outputting our deduplicated, clean, and merged datasets here during tomorrow's cleaning phase.
*   `notebooks/` - **Placeholder**. Set up and ready for Jupyter/Google Colab notebooks for explorative analysis.
*   `sql/` - **Placeholder**. Ready to hold database table definitions, schemas, and staging queries.
*   `dashboard/` - **Empty**. Another intentional placeholder. I'll be using this directory later to store the visual assets, styling sheets, and configuration files for the UI and dashboard widgets.
*   `reports/` - **Active**. Where I'm saving our documentation, summaries, and data quality reports.

### Quick Note on Environment:
I successfully initialized the local Git repository and set up the remote pointing to our GitHub repository. Everything has been committed cleanly under `"Day 1: Data ingestion complete"`. 

I also created `requirements.txt` with all the specific versions we need for the analytical stack (Pandas, NumPy, Matplotlib, Seaborn, Plotly, SQLAlchemy, Requests, SciPy, and Jupyter).

---

## 2. Ingested Datasets & Structural Profiles

I wrote an ETL script (`data_ingestion.py`) to systematically load and inspect all **10 source CSV files** using Pandas. Here is the exact profile of the data as it stands:

| Dataset File Name | Shape (Rows x Cols) | Target Primary Key | Main Column Dtypes | Quality Status |
| :--- | :---: | :--- | :--- | :---: |
| `fund_master.csv` | 12 x 6 | `amfi_code` | `int64`, `object` (string) | **Dirty** (Has nulls & duplicates) |
| `nav_history.csv` | 101 x 3 | `amfi_code` + `date` | `int64`, `object` (string), `float64` | **Dirty** (Mixed date formats) |
| `investors.csv` | 5 x 5 | `investor_id` | `object`, `object` (string) | **Dirty** (Has nulls) |
| `transactions.csv` | 6 x 7 | `transaction_id` | `object`, `int64`, `float64` | **Dirty** (Has nulls & duplicates) |
| `fund_managers.csv` | 4 x 4 | `manager_id` | `object`, `int64`, `object` | **Clean** |
| `portfolio_holdings.csv` | 5 x 5 | `holding_id` | `object`, `int64`, `float64` | **Clean** |
| `amc_details.csv` | 4 x 5 | `amc_id` | `object`, `int64`, `int64` | **Clean** |
| `expense_ratios.csv` | 4 x 4 | `amfi_code` | `int64`, `float64`, `float64` | **Clean** |
| `benchmarks.csv` | 4 x 3 | `benchmark_id` | `object`, `object`, `object` | **Clean** |
| `benchmark_history.csv` | 20 x 3 | `benchmark_id` + `date` | `object`, `object`, `float64` | **Clean** |

---

## 3. Data Quality & Anomalies Breakdown (The "Dirty" List)

While profiling the files, I detected several anomalies that will cause issues down the road if we don't fix them. Here is exactly what I found:

### A. Missing (Null) Values
*   **`fund_master.csv`**: There is **1 missing value** in the `risk_grade` column. It belongs to scheme `999999` ("Test Missing NAV Fund"). We should check if we can infer this or if it's just a dummy test record.
*   **`investors.csv`**: Investor `INV004` ("Bharath V") is **missing an email address**. Since we might need this for communication or unique lookups, we should note it.
*   **`transactions.csv`**: Transaction `TXN1004` is **missing the `units` value**. Luckily, we have the total transaction `amount` and can impute this by dividing the amount by the NAV value on the transaction date once we join the tables.

### B. Duplicate Records
*   **`fund_master.csv`**: Found **1 duplicate row** for HDFC Top 100 Fund (`amfi_code`: `125497`). It was written twice in the source.
*   **`transactions.csv`**: Transaction `TXN1001` was **duplicated** in the list. We need to drop this duplicate so we don't double-count sales or portfolio balances!

### C. Data Type and Format Inconsistencies
*   **Date Fields Read as Strings**: Currently, the date columns in `nav_history.csv`, `investors.csv`, `transactions.csv`, and `benchmark_history.csv` are being read as raw text objects. I'll need to parse these into actual `datetime` objects on Day 2 to allow proper sorting, grouping, and chronological analysis.
*   **Mixed Date Formats**: In `nav_history.csv`, a record for scheme `119551` was entered in the `DD/MM/YYYY` format, while everything else is in `YYYY-MM-DD`. This breaks basic string-based sorting and will cause date parsing to fail if we don't handle it with a flexible date parser.

---

## 4. AMFI Code Integrity & Cross-Validation

The **AMFI Scheme Code** is the unique 5-to-6 digit number assigned by the Association of Mutual Funds in India. It is our natural key to join the static fund metadata (like risk ratings, fund houses, categories) with price history or transactions.

I ran a relational check between our `fund_master.csv` unique codes and our `nav_history.csv` unique codes. I found two integrity issues:
1.  **Orphan Master Code**: AMFI Code `999999` ("Test Missing NAV Fund") exists in our fund master metadata but has **no daily price entries** in `nav_history.csv`.
2.  **Orphan NAV History Code**: AMFI Code `888888` has daily price values inside `nav_history.csv` but **does not exist in `fund_master.csv`**.

If we run a basic `INNER JOIN` in our SQL staging tables later, these records will be silently dropped. If we run a `LEFT JOIN` on `nav_history`, the orphan codes will have null details. Tomorrow, I will write a cleanup routine to decide whether to prune them or populate dummy names for them.

---

## 5. Live Ingestion Results from API (`mfapi.in`)

I wrote a small API tool (`live_nav_fetch.py`) to connect to the open API at `https://api.mfapi.in` and grab the live and historical NAV record sets. 

The script was fully successful, fetched all 6 schemes, and saved them as clean, individual CSVs under `data/raw/`:
*   **HDFC Top 100 Direct** (125497) -> `hdfc_top_100_direct_nav.csv` (3,091 records)
*   **SBI Bluechip** (119551) -> `sbi_bluechip_nav.csv` (3,236 records)
*   **ICICI Bluechip** (120503) -> `icici_bluechip_nav.csv` (3,307 records)
*   **Nippon Large Cap** (118632) -> `nippon_large_cap_nav.csv` (3,298 records)
*   **Axis Bluechip** (119092) -> `axis_bluechip_nav.csv` (3,565 records)
*   **Kotak Bluechip** (120841) -> `kotak_bluechip_nav.csv` (3,301 records)

---

## 6. What's Next (Tomorrow's Cleanup Plan)

To get these files ready for our database and dashboards, my plan for Day 2 is to:
1.  **Deduplicate**: Clean up the duplicate rows in `fund_master.csv` and `transactions.csv`.
2.  **Harmonize Dates**: Use a flexible parser to convert all date columns into standard `YYYY-MM-DD` datetime objects, fixing the mixed-format entry in NAV history.
3.  **Impute Missing Units**: Look up the NAV for Transaction `TXN1004` and calculate the missing unit count programmatically.
4.  **Align Keys**: Address the orphan codes (`999999` and `888888`) so that our database queries execute cleanly with full referential integrity.

Overall, the setup and ingestion went really well today. The data has a few typical real-world flaws, but they are all very manageable. Let me know if you have any questions or want me to tweak the cleaning plan for tomorrow!
