# Mutual Fund Analytics Platform 📈
### End-to-End Data Engineering & ETL Pipeline — Bluestock Capstone Project

Welcome to the **Mutual Fund Analytics Platform** Capstone Project repository, developed as part of the Bluestock Fintech Internship program. 

This repository leverages a clean **Monorepo Structure** to organize the end-to-end development of a financial analytics platform that ingests, cleans, stores, analyzes, and visualizes Indian Mutual Fund datasets.

---

## 📁 7-Day Monorepo Folder Structure

The repository is structured as a progressive daily monorepo. Each day's work is self-contained within its respective folder:

```text
bluestock-mutual-fund-analytics/
│
├── .git/
├── .gitignore
├── requirements.txt            # Unified project dependencies
├── README.md                   # Master repository documentation (You are here)
│
├── day 1/                      # Day 1: Project Setup + Data Ingestion (ETL)
│   ├── data_ingestion.py       # Local ETL bootstrapping, loading, & validation pipeline
│   ├── live_nav_fetch.py       # Live daily NAV fetcher from mfapi.in
│   ├── sql/                    # PostgreSQL DDL staging queries
│   ├── dashboard/              # Staging directory for dashboard assets
│   ├── notebooks/              # Jupyter research environment
│   ├── reports/                # Day 1 data quality reports & Word generator
│   └── README.md               # Day 1 documentation & workflows
│
├── day 2/                      # Day 2: Data Cleaning + SQLite Database Design
│   ├── data/                   # Self-contained Day 2 data directory
│   │   ├── raw/                # Raw source datasets (CSVs + Scraped JSONs)
│   │   └── processed/          # Downstream validated & forward-filled CSVs
│   ├── schema.sql              # Star Schema relational DDL (facts and dimensions)
│   ├── queries.sql             # 10 comprehensive analytical SQL queries
│   ├── db_loader.py            # SQLite database creation & insertion script
│   ├── execute_queries.py      # Automated SQL execution harness
│   ├── data_dictionary.md      # Database column reference and business definitions
│   └── bluestock_mf.db         # Loaded SQLite database instance (~10.5 MB)
│
├── day 3/                      # Day 3: Exploratory Data Analysis (EDA)
│   ├── EDA_Analysis.ipynb      # Main Jupyter notebook containing the 10 core analyses
│   └── charts/                 # 15 interactive and static data visualization assets
│
├── day 4/                      # Day 4: Mutual Fund Performance Analytics & Scorecard
│   ├── Performance_Analytics.ipynb # Main quantitative analytics Jupyter notebook
│   ├── reports/                # Computed risk-return tables
│   │   ├── alpha_beta.csv      # Alpha, Beta, R-squared & p-values OLS regression metrics
│   │   └── fund_scorecard.csv  # 0-100 composite scorecard & rankings
│   └── README.md               # Day 4 detailed performance & ranking documentation
│
└── day 5/                      # Day 5: Interactive BI Dashboard & Web Deployment
    ├── Dashboard.pdf           # Combined 4-page exported report
    ├── page_1.png to page_4.png # Individual page screenshots
    ├── dashboard/              # Streamlit application scripts
    ├── bluestock_mf_dashboard.pbix.pbip # Power BI project descriptor
    └── README.md               # Day 5 documentation & deployment guide
```

---

## 🚀 Progressive Project Roadmap

### 📅 [Day 1: Project Setup + Data Ingestion](file:///c:/Users/jibum/OneDrive/Desktop/Bluestock%20Internship/day%201/README.md)
*   **ETL Bootstrap Ingestion:** Completed local python pipeline in `day 1/data_ingestion.py` that auto-generates raw dataset structures and audits file metrics.
*   **Live NAV Fetcher:** Real-time JSON parser in `day 1/live_nav_fetch.py` scraping historical NAVs for 6 core mutual fund schemes directly from the public AMFI REST API (`mfapi.in`).
*   **Quality Reports:** Comprehensive data quality and referential integrity audit generated in `day 1/reports/day1_data_quality_summary.md`.

### 📅 [Day 2: Data Cleaning + SQLite DB Design](file:///c:/Users/jibum/OneDrive/Desktop/Bluestock%20Internship/day%202/data_dictionary.md)
*   **Robust Data Cleaning:** Implemented parsing, deduplication, anomaly boundaries, and daily continuous **forward-filling** for holiday/weekend NAV tracking in `day 2/data_cleaning.py`.
*   **Dimensional Star Schema:** Designed a normalized relational model in `day 2/schema.sql` spanning 2 dimension tables (`dim_fund`, `dim_date`) and 6 fact tables (`fact_nav`, `fact_transactions`, etc.).
*   **SQL Analytics:** Drafted 10 high-value business queries in `day 2/queries.sql` analyzing AUM trends, monthly average NAVs, YoY growth, and investor demographic cash flows.

### 📅 [Day 3: Exploratory Data Analysis](file:///c:/Users/jibum/OneDrive/Desktop/Bluestock%20Internship/day%203/EDA_Analysis.ipynb)
*   **Table Schema Ingestion**: Built connection handlers to load facts and dimensions dynamically into Pandas dataframes.
*   **10 Key Analytical Dashboards**: Generated 15 interactive charts (Plotly/Seaborn) analyzing historical NAVs, AUM growth, demographics, geographic distributions, folio growth, and correlation metrics.
*   **Insight Discovery**: Documented 10 key findings regarding folio-AUM elasticity, SIP ticket size distribution, and demographic concentrations.

### 📅 [Day 4: Mutual Fund Performance Analytics & Scorecard](file:///c:/Users/jibum/OneDrive/Desktop/Bluestock%20Internship/day%204/README.md)
*   **Quantitative Computations**: Coded multi-period CAGR calculations (1yr, 3yr, and 4.4yr proxies) and aligned NAV return series against Nifty 100 benchmark calendars.
*   **Risk-Adjusted Efficiency**: Computed annualized Sharpe and Sortino Ratios using excess returns relative to a 6.5% risk-free rate and downside deviation.
*   **OLS Benchmark Regressions**: Conducted regressions vs. Nifty 100, extracting Alpha (active outperformance), Beta (volatility factor), R-squared, and regression p-value significance.
*   **Composite Scoring**: Created a 0-100 scale investment ranking scorecard weighting 3yr CAGR (30%), Sharpe (25%), Alpha (20%), Expense Ratio (15%), and Max Drawdown (10%), with Mirae Asset Large Cap Fund scoring highest (85.90).

### 📅 [Day 5: Interactive BI Dashboard & Web Deployment](file:///c:/Users/jibum/OneDrive/Desktop/Bluestock%20Internship/day%205/README.md)
*   **Web Dashboard App**: Developed a 5-page Streamlit application reflecting Power BI analytics layout, matching Bluestock Fintech brand colors and typography.
*   **Star Schema Connection**: Integrated SQLite star schema to power real-time visualizations (AUM growth, risk-return scatters, geo-demographic transactions, and benchmark comparisons).
*   **Automated Exports**: Wrote Playwright-based browser automation to render and capture all dashboard views and compile a unified `Dashboard.pdf` report.

### 📅 [Day 6: Advanced Analytics & Risk Metrics](file:///c:/Users/jibum/OneDrive/Desktop/Bluestock%20Internship/Advanced_Analytics.ipynb)
*   **Downside Risk Analytics**: Computed 95% Historical Value at Risk (VaR) and Conditional Value at Risk (CVaR) across all 40 schemes, identifying small-cap funds as the highest-risk asset class.
*   **Rolling Sharpe Ratios**: Calculated and visualized rolling 90-day annualized Sharpe ratios over a 4-year period for 5 key funds to monitor change in risk-adjusted efficiency.
*   **Investor Cohort Analysis**: Categorized investors by their first transaction year (2024 vs. 2025), analyzing total gross/net invested capital and identifying average monthly SIP ticket sizes.
*   **SIP Continuity**: Evaluated chronological transaction intervals for long-term investors, flagging those with transaction gaps exceeding 35 days (revealing a 97.8% at-risk churn rate).
*   **Portfolio Concentration**: Calculated Sector Herfindahl-Hirschman Index (HHI) for equity portfolios, ranking funds from highly concentrated (Axis Bluechip, HHI = 2,967.69) to highly diversified (UTI Mid Cap, HHI = 1,240.20).
*   **Interactive Fund Recommender**: Built a command-line script (`recommender.py`) that matches investor risk appetite (`Low`/`Moderate`/`High`) to recommend the top 3 mutual funds sorted by Sharpe ratio.

---

## 🛠️ Technical Stack Details

*   **Language:** Python 3.10+ (Pandas, NumPy, Requests)
*   **Database Engine:** SQLite3
*   **SQL Interfaces:** standard SQLite SQL DDL
*   **ORM / Drivers:** Python-native SQLite3 connector
*   **Version Control:** Git + GitHub
