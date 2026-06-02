# Day 1 Data Quality Summary

## 1. Executive Ingestion Summary
On **Day 1** of the **Mutual Fund Analytics** Capstone Project, we completed the full implementation of the **Project Setup + Data Ingestion (ETL)** phase. The objective of this phase is to establish a robust directory structure, define the library requirements, ingest and inspect 10 local CSV datasets, fetch live NAV data for 6 key schemes, and execute structural validation checks. 

This summary report captures our setup details, file profiles, identified anomalies, and relational integrity observations.

---

## 2. Directory Structure & Environment
The project structure has been established directly inside the target directory `C:\Users\jibum\OneDrive\Desktop\Bluestock Internship`:
*   `data/raw/` - Contains the 10 local source CSV datasets and fetched live NAV data.
*   `data/processed/` - Prepared for downstream cleaned/aggregated tables (Day 2).
*   `notebooks/` - Staging folder for Jupyter and Colab explorations.
*   `sql/` - Dedicated folder for database table schemas and staging queries.
*   `dashboard/` - Staging folder for visualization assets and UI configurations.
*   `reports/` - Repository for documentation, data quality summaries, and reports.

### Environment Observations (Anomalies)
*   **Git command path warning:** A command command failure occurred when invoking `git init` because the git command-line tool was not registered in the system's PATH. Although the folders were successfully initialized, the workspace environment lacks an active local Git execution flow. This is documented as an environment configuration anomaly that should be resolved by installing or linking Git.

---

## 3. Python Dependencies (`requirements.txt`)
A unified `requirements.txt` has been created to support downstream analytical processing:
1.  **Pandas / NumPy:** For high-performance data manipulation and numerical operations.
2.  **Matplotlib / Seaborn / Plotly:** For advanced data visualization and dashboard rendering.
3.  **SQLAlchemy:** For relational database operations and query execution.
4.  **Requests:** For high-speed HTTP retrieval (e.g. fetching daily NAV data).
5.  **SciPy:** For statistics and advanced scientific computations.
6.  **Jupyter:** For scratch workspace execution.

---

## 4. Ingested Datasets Profile
We successfully loaded and profiled all **10 source CSV datasets** in our ingestion script `data_ingestion.py`. The profiles (shape, key data types, and primary keys) are detailed below:

| # | Dataset Name | Shape (Rows x Cols) | Primary Key / Relational Keys | Key Column Dtypes |
|---|--------------|---------------------|-------------------------------|-------------------|
| 1 | `fund_master.csv` | 12 x 6 | `amfi_code` | `amfi_code` (int64), `scheme_name` (object), `fund_house` (object), `category` (object) |
| 2 | `nav_history.csv` | 101 x 3 | `amfi_code`, `date` | `amfi_code` (int64), `date` (object), `nav` (float64) |
| 3 | `investors.csv` | 5 x 5 | `investor_id` | `investor_id` (object), `name` (object), `risk_profile` (object), `joined_date` (object) |
| 4 | `transactions.csv` | 6 x 6 | `transaction_id` | `transaction_id` (object), `investor_id` (object), `amfi_code` (int64), `amount` (float64) |
| 5 | `fund_managers.csv` | 4 x 4 | `manager_id` | `manager_id` (object), `name` (object), `experience_years` (int64), `qualification` (object) |
| 6 | `portfolio_holdings.csv` | 5 x 5 | `holding_id` | `holding_id` (object), `amfi_code` (int64), `stock_name` (object), `allocation_percentage` (float64) |
| 7 | `amc_details.csv` | 4 x 5 | `amc_id` | `amc_id` (object), `fund_house` (object), `ceo` (object), `aum_in_crores` (int64) |
| 8 | `expense_ratios.csv` | 4 x 4 | `amfi_code` | `amfi_code` (int64), `expense_ratio` (float64), `exit_load` (float64), `turnover_ratio` (float64) |
| 9 | `benchmarks.csv` | 4 x 3 | `benchmark_id` | `benchmark_id` (object), `benchmark_name` (object), `index_type` (object) |
| 10 | `benchmark_history.csv` | 20 x 3 | `benchmark_id`, `date` | `benchmark_id` (object), `date` (object), `index_value` (float64) |

---

## 5. Data Quality & Anomalies Report
During dataset ingestion and exploratory inspection, several structural and quality anomalies were detected:

### A. Missing (Null) Values
*   **`fund_master.csv`:** Found **1 null value** in the `risk_grade` column (for AMFI code `999999` / "Test Missing NAV Fund").
*   **`investors.csv`:** Found **1 null value** in the `email` column (for Investor `INV004` / "Bharath V").
*   **`transactions.csv`:** Found **1 null value** in the `units` column (for Transaction `TXN1004` / Investor `INV004`).

### B. Duplicate Rows
*   **`fund_master.csv`:** Found **1 duplicate row** (AMFI code `125497` / "HDFC Top 100 Fund" exists twice).
*   **`transactions.csv`:** Found **1 duplicate transaction row** (Transaction `TXN1001` is duplicated).

### C. Datatype Anomalies
*   **Date columns loaded as objects (strings):** In `nav_history.csv`, `investors.csv`, `transactions.csv`, and `benchmark_history.csv`, the date columns are read as raw string objects. In Day 2 cleanups, these must be parsed using `pd.to_datetime()` to support sorting and historical queries.
*   **Mixed Date Formats:** In `nav_history.csv`, one record for scheme `119551` was formatted as `DD/MM/YYYY`, while others were formatted as `YYYY-MM-DD`. This causes inconsistencies during simple string sorting.

---

## 6. Fund Master & AMFI Code Architecture
The exploratory analysis of `fund_master.csv` revealed the following structural details:

### A. Fund Master Dimensions
*   **Unique Fund Houses (AMCs):** HDFC Mutual Fund, SBI Mutual Fund, ICICI Prudential Mutual Fund, Nippon India Mutual Fund, Axis Mutual Fund, Kotak Mahindra Mutual Fund, PPFAS Mutual Fund, Ghost Mutual Fund.
*   **Unique Scheme Categories:** Equity, Debt.
*   **Unique Scheme Sub-Categories:** Large Cap, Mid Cap, Small Cap, Flexi Cap, Liquid.
*   **Unique Risk Grades:** Very High, High.

### B. AMFI Scheme Code Structure
The **AMFI Scheme Code** is a standardized 5-to-6 digit numeric string utilized throughout the Indian mutual fund industry:
1.  **Unique Scheme Identifier:** Acts as a uniform primary key. Since scheme names vary across portals, the numeric AMFI code is critical to ensure accurate scheme identification.
2.  **Relational Database Key:** Serves as the natural key to join static metadata (scheme details, expense ratios, portfolio allocations) with historical daily transaction and price (NAV) details.
3.  **Data Ingestion Integration:** A core parameter used in external APIs (e.g. `mfapi.in`) to fetch daily NAV series.

---

## 7. AMFI Code Consistency Validation
We executed a relational integrity validation matching `fund_master.csv` against `nav_history.csv`:

*   **Total unique AMFI codes in Fund Master:** 11
*   **Total unique AMFI codes in NAV History:** 11
*   **Validation Mismatches Detected:**
    *   **Orphan Master Codes (Missing in NAV History):** Code `999999` ("Test Missing NAV Fund") exists in `fund_master.csv` but has **no matching daily values** in `nav_history.csv`.
    *   **Orphan History Codes (Missing in Master):** Code `888888` has daily price values in `nav_history.csv` but **no metadata record** in `fund_master.csv`.

> [!WARNING]
> Relational joins executed on these mismatched codes will result in information loss (omitted records during `INNER JOIN` or orphan null entries in `LEFT JOIN`). Cleanups should involve pruning these orphan records or mapping them correctly.

---

## 8. Live Ingestion Results (`mfapi.in`)
The live NAV ingestion script `live_nav_fetch.py` successfully completed the download of live data for 6 key schemes:
1.  **HDFC Top 100 Direct** (125497)
2.  **SBI Bluechip** (119551)
3.  **ICICI Bluechip** (120503)
4.  **Nippon Large Cap** (118632)
5.  **Axis Bluechip** (119092)
6.  **Kotak Bluechip** (120841)

All fetched records have been successfully saved as individual raw CSV files in `data/raw/` for downstream aggregation.

---

## 9. Downstream Cleanup Plan (Day 2)
To prepare these ingested datasets for database loading and dashboarding, we will execute the following steps in Day 2:
1.  **Deduplication:** Drop duplicate records in `fund_master.csv` and `transactions.csv`.
2.  **Datatype Parsing:** Convert all date string columns to native datetime objects.
3.  **Null Imputation:** Resolve nulls in `units` by recalculating `amount / NAV` at the transaction date, and populate `risk_grade` using standard subclass references.
4.  **Relational Alignment:** Align unmatched AMFI codes or prune orphan rows to ensure referential integrity.
