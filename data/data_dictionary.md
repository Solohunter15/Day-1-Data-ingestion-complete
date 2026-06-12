# Data Dictionary: Mutual Fund Analytics Star Schema

This document details the tables, columns, data types, business definitions, and references for the SQLite database **`bluestock_mf.db`** designed for the Bluestock Mutual Fund Analytics Platform.

---

## 1. `dim_fund` (Dimension Table)
*   **Description**: Stores the master metadata for each mutual fund scheme.
*   **Primary Key**: `amfi_code` (INTEGER)

| Column Name | SQLite Data Type | Description | Source Field | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Unique AMFI code of the scheme (PK) | `amfi_code` | `119551` |
| `fund_house` | TEXT | Name of the Asset Management Company (AMC) | `fund_house` | `SBI Mutual Fund` |
| `scheme_name` | TEXT | Full name of the mutual fund scheme | `scheme_name` | `SBI Bluechip Fund - Regular Plan` |
| `category` | TEXT | Asset class category (Equity / Debt) | `category` | `Equity` |
| `sub_category` | TEXT | SEBI fund sub-category | `sub_category` | `Large Cap` |
| `plan` | TEXT | Plan type (Regular / Direct) | `plan` | `Regular` |
| `launch_date` | TEXT | Launch date of the scheme (YYYY-MM-DD) | `launch_date` | `2006-02-14` |
| `benchmark` | TEXT | Official index benchmark for comparison | `benchmark` | `NIFTY 100 TRI` |
| `expense_ratio_pct` | REAL | Total Expense Ratio (TER) in percentage | `expense_ratio_pct` | `1.54` |
| `exit_load_pct` | REAL | Exit load penalty in percentage | `exit_load_pct` | `1.0` |
| `min_sip_amount` | INTEGER | Minimum allowed SIP installment amount | `min_sip_amount` | `500` |
| `min_lumpsum_amount`| INTEGER | Minimum allowed lumpsum purchase amount | `min_lumpsum_amount`| `1000` |
| `fund_manager` | TEXT | Name of the primary fund portfolio manager | `fund_manager` | `Sohini Andani` |
| `risk_category` | TEXT | SEBI Riskometer grade rating | `risk_category` | `Moderate` |
| `sebi_category_code`| TEXT | Internal SEBI category reference key | `sebi_category_code`| `EC01` |

---

## 2. `dim_date` (Dimension Table)
*   **Description**: Stores dates to enable calendar slicing, sorting, and chronological trends.
*   **Primary Key**: `date` (TEXT)

| Column Name | SQLite Data Type | Description | Generation Method | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `date` | TEXT | Date in ISO format (YYYY-MM-DD) (PK) | Date series generation | `2024-01-03` |
| `year` | INTEGER | Calendar year | Date extraction | `2024` |
| `month` | INTEGER | Month number (1 to 12) | Date extraction | `1` |
| `quarter` | INTEGER | Fiscal/calendar quarter (1 to 4) | Date extraction | `1` |
| `is_weekday` | INTEGER | Weekday flag (1 = Weekday, 0 = Weekend) | Day-of-week extraction | `1` |

---

## 3. `fact_nav` (Fact Table)
*   **Description**: Holds daily Net Asset Value (NAV) time-series facts for all funds.
*   **Foreign Keys**: `amfi_code` (references `dim_fund`), `date` (references `dim_date`)
*   **Composite Primary Key**: (`amfi_code`, `date`)

| Column Name | SQLite Data Type | Description | Source Field | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Foreign key referencing fund master (PK part 1) | `amfi_code` | `119551` |
| `date` | TEXT | Foreign key referencing date dimension (PK part 2) | `date` | `2022-01-03` |
| `nav` | REAL | Net Asset Value in Rupees (forward-filled) | `nav` | `54.3856` |

---

## 4. `fact_transactions` (Fact Table)
*   **Description**: Contains details of individual investor purchase, redemption, and SIP transactions.
*   **Primary Key**: `tx_id` (INTEGER AUTOINCREMENT)
*   **Foreign Keys**: `amfi_code` (references `dim_fund`), `transaction_date` (references `dim_date`)

| Column Name | SQLite Data Type | Description | Source Field | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `tx_id` | INTEGER | Autoincremented transaction key (PK) | Generated index | `1` |
| `investor_id` | TEXT | Unique investor identification string | `investor_id` | `INV003054` |
| `transaction_date` | TEXT | Date of transaction (FK) | `transaction_date` | `2024-01-01` |
| `amfi_code` | INTEGER | Scheme code of purchase (FK) | `amfi_code` | `119092` |
| `transaction_type` | TEXT | Transaction category (SIP / Lumpsum / Redemption) | `transaction_type` | `SIP` |
| `amount_inr` | INTEGER | Total transaction size in Rupees | `amount_inr` | `1834` |
| `state` | TEXT | Residence state of the investor | `state` | `Telangana` |
| `city` | TEXT | Residence city of the investor | `city` | `Hyderabad` |
| `city_tier` | TEXT | Classification of city tier (T30 / B30) | `city_tier` | `T30` |
| `age_group` | TEXT | Age range bucket of the investor | `age_group` | `56+` |
| `gender` | TEXT | Gender of the investor | `gender` | `Female` |
| `annual_income_lakh`| REAL | Annual declared income in Rs. lakh | `annual_income_lakh`| `77.1` |
| `payment_mode` | TEXT | Mode used (UPI / Net Banking / Mandate / Cheque) | `payment_mode` | `UPI` |
| `kyc_status` | TEXT | Compliance KYC Status (Verified / Pending) | `kyc_status` | `Verified` |

---

## 5. `fact_performance` (Fact Table)
*   **Description**: Stores static scheme risk, return, volatility, and score values.
*   **Primary Key / FK**: `amfi_code` (references `dim_fund`)

| Column Name | SQLite Data Type | Description | Source Field | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Unique scheme code mapping to fund master (PK) | `amfi_code` | `119551` |
| `scheme_name` | TEXT | Name of the fund scheme | `scheme_name` | `SBI Bluechip Fund` |
| `fund_house` | TEXT | Name of the Asset Management Company | `fund_house` | `SBI Mutual Fund` |
| `category` | TEXT | Category classification of fund returns | `category` | `Equity` |
| `plan` | TEXT | Direct or Regular indicator | `plan` | `Regular` |
| `return_1yr_pct` | REAL | 1-Year absolute return in percentage | `return_1yr_pct` | `12.45` |
| `return_3yr_pct` | REAL | 3-Year Compounded Annualised Growth Rate (CAGR) | `return_3yr_pct` | `14.82` |
| `return_5yr_pct` | REAL | 5-Year CAGR | `return_5yr_pct` | `16.50` |
| `benchmark_3yr_pct` | REAL | Benchmark returns over 3 years | `benchmark_3yr_pct` | `13.12` |
| `alpha` | REAL | Risk-adjusted return outperformance (vs benchmark) | `alpha` | `1.70` |
| `beta` | REAL | Volatility sensitivity to benchmark index (1.0 = equal) | `beta` | `0.95` |
| `sharpe_ratio` | REAL | Sharpe risk-adjusted return ratio (higher is better) | `sharpe_ratio` | `1.15` |
| `sortino_ratio` | REAL | Sortino risk-adjusted return ratio (penalizes only downside) | `sortino_ratio` | `1.42` |
| `std_dev_ann_pct` | REAL | Annualised standard deviation of returns (%) | `std_dev_ann_pct` | `12.80` |
| `max_drawdown_pct` | REAL | Peak-to-trough worst-case loss (%) | `max_drawdown_pct` | `-15.20` |
| `aum_crore` | INTEGER | Active Assets under Management in Rupees crore | `aum_crore` | `43200` |
| `expense_ratio_pct` | REAL | Total Expense Ratio (TER) in percentage | `expense_ratio_pct` | `1.54` |
| `morningstar_rating`| INTEGER | Rating stars from 1 (lowest) to 5 (highest) | `morningstar_rating`| `4` |
| `risk_grade` | TEXT | Category risk evaluation | `risk_grade` | `Moderate` |

---

## 6. `fact_aum` (Fact Table)
*   **Description**: Stores quarterly Assets Under Management (AUM) benchmarks per AMC.
*   **Composite Primary Key**: (`date`, `fund_house`)
*   **Foreign Key**: `date` (references `dim_date`)

| Column Name | SQLite Data Type | Description | Source Field | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `date` | TEXT | Foreign key date of reporting quarter (PK part 1) | `date` | `2022-03-31` |
| `fund_house` | TEXT | Asset Management Company name (PK part 2) | `fund_house` | `SBI Mutual Fund` |
| `aum_lakh_crore` | REAL | Total AMC AUM in Rs. lakh crore | `aum_lakh_crore` | `6.05` |
| `aum_crore` | INTEGER | Total AMC AUM in Rs. crore | `aum_crore` | `605000` |
| `num_schemes` | INTEGER | Number of active schemes managed by the AMC | `num_schemes` | `186` |

---

## 7. `fact_portfolio` (Fact Table)
*   **Description**: Stores portfolio weight allocations for all tracked equity funds.
*   **Composite Primary Key**: (`amfi_code`, `stock_symbol`)
*   **Foreign Key**: `amfi_code` (references `dim_fund`)

| Column Name | SQLite Data Type | Description | Source Field | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Foreign key referencing fund master (PK part 1) | `amfi_code` | `119551` |
| `stock_symbol` | TEXT | Stock ticker symbol in the exchange portfolio (PK part 2) | `stock_symbol` | `POWERGRID` |
| `stock_name` | TEXT | Official registered company name | `stock_name` | `Power Grid Corp.` |
| `sector` | TEXT | Company industry sector category | `sector` | `Utilities` |
| `weight_pct` | REAL | Allocation weight of equity holdings in percentage | `weight_pct` | `6.25` |
| `market_value_cr` | REAL | Market holding size in Rs. crore | `market_value_cr` | `2700` |
| `current_price_inr` | REAL | Latest share price in Indian Rupees | `current_price_inr` | `6011.08` |
| `portfolio_date` | TEXT | Closing date of holdings metrics (YYYY-MM-DD) | `portfolio_date` | `2025-12-31` |

---

## 8. `fact_sip_industry` (Fact Table)
*   **Description**: Contains monthly aggregate mutual fund industry SIP inflows.
*   **Primary Key**: `month` (TEXT)

| Column Name | SQLite Data Type | Description | Source Field | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `month` | TEXT | Calendar reporting month in YYYY-MM format (PK) | `month` | `2022-01` |
| `sip_inflow_crore` | INTEGER | Aggregate monthly SIP inflows in Rs. crore | `sip_inflow_crore` | `11517` |
| `active_sip_accounts_crore` | REAL | Number of active SIP accounts contributing (in crore) | `active_sip_accounts_crore` | `4.80` |
| `new_sip_accounts_lakh` | REAL | New SIP account registrations in lakh | `new_sip_accounts_lakh` | `22.40` |
| `sip_aum_lakh_crore` | REAL | Industry aggregate SIP AUM in Rs. lakh crore | `sip_aum_lakh_crore` | `4.80` |
| `yoy_growth_pct` | REAL | Month-over-Month YoY growth rate (0.0 if missing) | `yoy_growth_pct` | `15.5` |
