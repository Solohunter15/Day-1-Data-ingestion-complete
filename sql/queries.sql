-- ====================================================================
-- SQLite Analytical Queries: Mutual Fund Analytics Platform
-- Day 2 - SQL Analytics
-- ====================================================================

-- 1. Top 5 funds by AUM
SELECT 
    f.amfi_code, 
    f.scheme_name, 
    f.fund_house, 
    p.aum_crore
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month for SBI Bluechip Fund (amfi_code: 119551)
SELECT 
    d.year, 
    d.month, 
    ROUND(AVG(n.nav), 4) as avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.date
WHERE n.amfi_code = 119551
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 3. Monthly SIP Inflow and YoY Growth (Industry Trend)
SELECT 
    month, 
    sip_inflow_crore, 
    active_sip_accounts_crore, 
    yoy_growth_pct
FROM fact_sip_industry
ORDER BY month;

-- 4. Transactions count and total amount in Rs. grouped by state
SELECT 
    state, 
    COUNT(*) as txn_count, 
    SUM(amount_inr) as total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratio < 1.0% in Direct Plan
SELECT 
    amfi_code, 
    scheme_name, 
    fund_house,
    category,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0 AND plan = 'Direct'
ORDER BY expense_ratio_pct;

-- 6. Unique count of investors by city tier (T30 vs B30)
SELECT 
    city_tier, 
    COUNT(DISTINCT investor_id) as unique_investor_count
FROM fact_transactions
GROUP BY city_tier;

-- 7. Total transaction amount by gender and age group
SELECT 
    gender, 
    age_group, 
    SUM(amount_inr) as total_amount_inr,
    COUNT(*) as txn_count
FROM fact_transactions
GROUP BY gender, age_group
ORDER BY gender, age_group;

-- 8. Sector allocation summary across all portfolio holdings
SELECT 
    sector, 
    ROUND(SUM(weight_pct), 2) as aggregate_weight_pct,
    COUNT(DISTINCT amfi_code) as holding_funds_count
FROM fact_portfolio
GROUP BY sector
ORDER BY aggregate_weight_pct DESC;

-- 9. Average annualised 3yr return and Sharpe ratio by fund category
SELECT 
    category, 
    ROUND(AVG(return_3yr_pct), 2) as avg_3yr_return_pct, 
    ROUND(AVG(sharpe_ratio), 2) as avg_sharpe_ratio
FROM fact_performance
GROUP BY category;

-- 10. Net transaction cash flow (Total Inflows - Total Redemptions) per fund category
SELECT 
    f.category,
    SUM(CASE WHEN t.transaction_type IN ('SIP', 'Lumpsum') THEN t.amount_inr ELSE 0 END) as total_inflows_inr,
    SUM(CASE WHEN t.transaction_type = 'Redemption' THEN t.amount_inr ELSE 0 END) as total_outflows_inr,
    SUM(CASE WHEN t.transaction_type IN ('SIP', 'Lumpsum') THEN t.amount_inr ELSE -t.amount_inr END) as net_cash_flow_inr
FROM fact_transactions t
JOIN dim_fund f ON t.amfi_code = f.amfi_code
GROUP BY f.category
ORDER BY net_cash_flow_inr DESC;
