-- ====================================================================
-- SQLite Schema DDL: Mutual Fund Analytics Platform
-- Star Schema Design
-- ====================================================================

PRAGMA foreign_keys = ON;

-- 1. dim_fund: Static fund reference details
DROP TABLE IF EXISTS dim_fund;
CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    plan TEXT NOT NULL,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount INTEGER,
    min_lumpsum_amount INTEGER,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- 2. dim_date: Date dimension for clean chronological groupings
DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    is_weekday INTEGER NOT NULL -- 1 for Weekday, 0 for Weekend/Holiday
);

-- 3. fact_nav: Daily historical NAV facts
DROP TABLE IF EXISTS fact_nav;
CREATE TABLE fact_nav (
    amfi_code INTEGER NOT NULL,
    date TEXT NOT NULL,
    nav REAL NOT NULL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

-- 4. fact_transactions: Investor transactions facts
DROP TABLE IF EXISTS fact_transactions;
CREATE TABLE fact_transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type TEXT NOT NULL, -- SIP / Lumpsum / Redemption
    amount_inr INTEGER NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT, -- T30 / B30
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date)
);

-- 5. fact_performance: Scheme performance & risk metrics facts
DROP TABLE IF EXISTS fact_performance;
CREATE TABLE fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    category TEXT NOT NULL,
    plan TEXT NOT NULL,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore INTEGER,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- 6. fact_aum: AMC Quarterly AUM details facts
DROP TABLE IF EXISTS fact_aum;
CREATE TABLE fact_aum (
    date TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore INTEGER,
    num_schemes INTEGER,
    PRIMARY KEY (date, fund_house),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

-- 7. fact_portfolio: Top stock holding allocations facts
DROP TABLE IF EXISTS fact_portfolio;
CREATE TABLE fact_portfolio (
    amfi_code INTEGER NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    weight_pct REAL NOT NULL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date TEXT NOT NULL,
    PRIMARY KEY (amfi_code, stock_symbol),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- 8. fact_sip_industry: Monthly aggregate industry flows facts
DROP TABLE IF EXISTS fact_sip_industry;
CREATE TABLE fact_sip_industry (
    month TEXT PRIMARY KEY,
    sip_inflow_crore INTEGER NOT NULL,
    active_sip_accounts_crore REAL NOT NULL,
    new_sip_accounts_lakh REAL NOT NULL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL NOT NULL
);

-- Indexes to optimize queries
CREATE INDEX IF NOT EXISTS idx_nav_amfi ON fact_nav(amfi_code);
CREATE INDEX IF NOT EXISTS idx_nav_date ON fact_nav(date);
CREATE INDEX IF NOT EXISTS idx_txn_date ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_txn_amfi ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_portfolio_amfi ON fact_portfolio(amfi_code);
