# Day 1 Data Ingestion & Quality Summary

## Bluestock Fintech - Mutual Fund Analytics Platform
**Prepared by**: Data Analyst Intern
**Date**: June 2026
**Project Phase**: Day 1 (Project Setup + Data Ingestion ETL)

---

## 1. Project Directory & Environment Layout

I have successfully initialized and verified the project folder structure inside `C:\Users\jibum\OneDrive\Desktop\Bluestock Internship`. 

Here is the current layout and directory status:
*   `data/raw/` - **Active**. This contains the 10 original local CSV datasets prefixed with `01_` through `10_`, along with the raw historical CSV files fetched from the public AMFI API.
*   `data/processed/` - **Staging**. Staging folder created. Deduped, clean, and merged datasets will be outputted here during the Day 2 cleaning phase.
*   `notebooks/` - **Placeholder**. Ready for Jupyter / Google Colab EDA notebooks.
*   `sql/` - **Placeholder**. Ready for database schema definition DDL scripts (`schema.sql`) and testing queries.
*   `dashboard/` - **Staging**. Staging folder for Power BI visual assets and exported layouts.
*   `reports/` - **Active**. Holds all analyst documentation and summary reports (including this document).

### Environment Details:
- The local Git repository has been initialized with all Day 1 scripts and reports tracked.
- The `requirements.txt` has been structured with explicit version bounds for `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `sqlalchemy`, `requests`, `scipy`, and `jupyter`.

---

## 2. Ingested Datasets & Structural Profiles

We performed a deep inspection of all **10 pre-packaged CSV datasets** provided for the Capstone project. The results are highly encouraging, showing a complete, production-grade dataset with excellent relational integrity.

| Dataset File Name | Shape (Rows x Cols) | Key Columns / Identifiers | Primary Key / Index Fields | Data Quality Status |
| :--- | :---: | :--- | :--- | :---: |
| `01_fund_master.csv` | 40 x 15 | `amfi_code`, `scheme_name`, `fund_house`, `category`, `sub_category`, `risk_category` | `amfi_code` | **Clean** (No nulls, no duplicates) |
| `02_nav_history.csv` | 46,000 x 3 | `amfi_code`, `date`, `nav` | `amfi_code` + `date` | **Clean** (No nulls, no duplicates) |
| `03_aum_by_fund_house.csv` | 90 x 5 | `date`, `fund_house`, `aum_lakh_crore`, `aum_crore`, `num_schemes` | `date` + `fund_house` | **Clean** (No nulls, no duplicates) |
| `04_monthly_sip_inflows.csv` | 48 x 6 | `month`, `sip_inflow_crore`, `active_sip_accounts_crore`, `yoy_growth_pct` | `month` | **Minor Anomaly** (Expected nulls) |
| `05_category_inflows.csv` | 144 x 3 | `month`, `category`, `net_inflow_crore` | `month` + `category` | **Clean** (No nulls, no duplicates) |
| `06_industry_folio_count.csv` | 21 x 6 | `month`, `total_folios_crore`, `equity_folios_crore`, `debt_folios_crore` | `month` | **Clean** (No nulls, no duplicates) |
| `07_scheme_performance.csv` | 40 x 19 | `amfi_code`, `scheme_name`, `alpha`, `beta`, `sharpe_ratio`, `risk_grade` | `amfi_code` | **Clean** (No nulls, no duplicates) |
| `08_investor_transactions.csv` | 32,778 x 13 | `investor_id`, `transaction_date`, `amfi_code`, `amount_inr`, `kyc_status` | `investor_id` + `transaction_date` | **Clean** (No nulls, no duplicates) |
| `09_portfolio_holdings.csv` | 322 x 8 | `amfi_code`, `stock_symbol`, `stock_name`, `sector`, `weight_pct` | `amfi_code` + `stock_symbol` | **Clean** (No nulls, no duplicates) |
| `10_benchmark_indices.csv` | 8,050 x 3 | `date`, `index_name`, `close_value` | `date` + `index_name` | **Clean** (No nulls, no duplicates) |

---

## 3. Data Quality & Anomalies Breakdown

An automated validation script ran a series of sanity checks across all 10 datasets:
1. **Missing (Null) Values Check**: Scanning for empty strings or `NaN` markers.
2. **Duplicate Records Check**: Scanning for completely identical rows.
3. **Data Type Consistency Check**: Inspecting date columns and numeric types.

### Key Quality Findings:

*   **`04_monthly_sip_inflows.csv`**: Contains **12 null values** in the `yoy_growth_pct` column. This is a mathematically expected anomaly rather than a data capture error. Because the dataset starts in January 2022, calculating Year-over-Year (YoY) growth is impossible for the first 12 months (Jan 2022 to Dec 2022) as it lacks baseline historical data from 2021.
*   **Duplicate Rows**: **None detected**. All datasets are cleanly indexed without repeating entries.
*   **Data Types**: The date fields are read as strings/objects during initial CSV load. These must be parsed into pandas `datetime64` objects in the processing scripts to enable chronological sorting.
*   **Portfolio Holdings Limit**: In `09_portfolio_holdings.csv`, only **34 unique AMFI codes** are present (out of the 40 total master funds). This is also a correct reflection of industry realities: holdings weights are only tracked for the 34 equity and index schemes; the remaining 6 debt/liquid schemes do not hold equity equities and are naturally omitted from this stock weight file.

---

## 4. AMFI Code Integrity & Cross-Validation

The **AMFI Scheme Code** is the unique 5-to-6 digit identifier issued by the Association of Mutual Funds in India. It serves as our natural joining key to connect static attributes (AMC details, exit loads, expense categories) with highly dynamic fact tables (price history, daily NAVs, investor transactions, and portfolio holdings).

A relational check was conducted between the unique AMFI code sets in `01_fund_master.csv` and `02_nav_history.csv` to ensure structural alignment:
*   **Total unique AMFI codes in Fund Master**: 40
*   **Total unique AMFI codes in NAV History**: 40
*   **Relational Match Result**: **100% Match (SUCCESS)**. Every single AMFI code listed in the master file has associated historical prices in the daily NAV history, and there are no orphan NAV records. This guarantees full referential integrity for database imports.

---

## 5. Live Ingestion Results from API (`mfapi.in`)

To enrich our analytical model with real-time variables, we developed `live_nav_fetch.py` to retrieve up-to-date and complete historical NAV arrays from the open API at `https://api.mfapi.in`. 

The ingestion pipeline succeeded with a 100% success rate, pulling down all 6 major fund classes and saving them as fresh CSV outputs under `data/raw/`:
1.  **HDFC Top 100 Direct** (125497) -> `hdfc_top_100_direct_nav.csv` (3,091 daily rows)
2.  **SBI Bluechip** (119551) -> `sbi_bluechip_nav.csv` (3,236 daily rows)
3.  **ICICI Prudential Bluechip** (120503) -> `icici_bluechip_nav.csv` (3,307 daily rows)
4.  **Nippon India Large Cap** (118632) -> `nippon_large_cap_nav.csv` (3,298 daily rows)
5.  **Axis Bluechip** (119092) -> `axis_bluechip_nav.csv` (3,565 daily rows)
6.  **Kotak Bluechip** (120841) -> `kotak_bluechip_nav.csv` (3,301 daily rows)

---

## 6. Next Steps: Day 2 Database Design & Loading

With the raw data ingested and verified, we are fully prepared to proceed to Day 2:
1.  **Date Parsing & Standardisation**: Implement standard `YYYY-MM-DD` date conversions across all staging models.
2.  **Staging SQL Schema**: Write DDL scripts in `sql/schema.sql` to establish a relational 5-table Star Schema in SQLite (`bluestock_mf.db`).
3.  **ETL Load Process**: Write an automated Python pipeline using SQLAlchemy to clean, structure, and load all 10 CSV tables into their respective dimension and fact SQLite tables.
4.  **Analytical SQL Testing**: Draft and execute the 10 core analytical queries (such as Top 5 funds by AUM, transaction volume counts by state, SIP YoY growth) to check database performance and verify calculations.
